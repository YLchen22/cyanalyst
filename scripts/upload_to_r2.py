# -*- coding: utf-8 -*-
"""CyAnalyst — Cloudflare R2 上传脚本

使用 S3 兼容 API 将研报文件上传至 Cloudflare R2。
依赖: boto3 (pip install boto3)
凭据从 .env 文件或环境变量读取。

用法:
  # 上传单个文件
  python upload_to_r2.py local_file.docx research/daily/2026-06-24-morning.docx

  # 上传整个目录（递归）
  python upload_to_r2.py --dir scripts/output research/

  # 列出 bucket 中已有文件
  python upload_to_r2.py --list

  # 测试连接
  python upload_to_r2.py --test
"""

import os
import sys
import mimetypes
from pathlib import Path

try:
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print("[ERROR] 缺少依赖 boto3，请运行: pip install boto3")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv 可选，环境变量也可直接设置


# ==================== 配置 ====================

R2_ACCOUNT_ID = os.environ.get("R2_ACCOUNT_ID", "")
R2_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY = os.environ.get("R2_SECRET_ACCESS_KEY", "")
R2_BUCKET_NAME = os.environ.get("R2_BUCKET_NAME", "cyanalyst-reports")
R2_PUBLIC_URL = os.environ.get("R2_PUBLIC_URL", "")  # e.g. https://pub-xxxx.r2.dev


def get_r2_client():
    """创建 R2 S3 兼容客户端"""
    if not R2_ACCOUNT_ID:
        print("[ERROR] 未设置 R2_ACCOUNT_ID")
        sys.exit(1)
    if not R2_ACCESS_KEY_ID or not R2_SECRET_ACCESS_KEY:
        print("[ERROR] 未设置 R2_ACCESS_KEY_ID 或 R2_SECRET_ACCESS_KEY")
        sys.exit(1)

    endpoint_url = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
        config=Config(
            retries={"max_attempts": 3, "mode": "standard"},
            connect_timeout=10,
            read_timeout=60,
        ),
    )


# ==================== 核心功能 ====================

def upload_file(local_path: str, remote_key: str) -> str:
    """上传单个文件到 R2

    Args:
        local_path: 本地文件路径
        remote_key: R2 中的对象 key（如 research/daily/2026-06-24.docx）

    Returns:
        文件的公共访问 URL
    """
    if not os.path.isfile(local_path):
        print(f"[ERROR] 文件不存在: {local_path}")
        return ""

    client = get_r2_client()
    file_size = os.path.getsize(local_path)

    # 根据扩展名设置 Content-Type
    content_type, _ = mimetypes.guess_type(local_path)
    if content_type is None:
        content_type = "application/octet-stream"

    extra_args = {
        "ContentType": content_type,
    }

    print(f"  Uploading: {local_path} ({file_size:,} bytes)")
    print(f"  -> r2://{R2_BUCKET_NAME}/{remote_key}")

    try:
        client.upload_file(
            local_path,
            R2_BUCKET_NAME,
            remote_key,
            ExtraArgs=extra_args,
        )
        print(f"  [OK] Upload successful")

        # 构建公共 URL
        if R2_PUBLIC_URL:
            public_url = f"{R2_PUBLIC_URL.rstrip('/')}/{remote_key}"
        else:
            public_url = f"https://{R2_BUCKET_NAME}.r2.dev/{remote_key}"

        print(f"  URL: {public_url}")
        return public_url

    except ClientError as e:
        print(f"  [FAIL] {e}")
        return ""
    except NoCredentialsError:
        print("  [FAIL] 凭据无效，请检查 .env 中的 R2 配置")
        return ""


def upload_directory(local_dir: str, remote_prefix: str) -> list:
    """递归上传目录下所有文件

    Args:
        local_dir: 本地目录路径
        remote_prefix: R2 中的前缀（如 research/daily/）

    Returns:
        上传成功的 URL 列表
    """
    if not os.path.isdir(local_dir):
        print(f"[ERROR] 目录不存在: {local_dir}")
        return []

    urls = []
    local_dir = os.path.abspath(local_dir)

    for root, dirs, files in os.walk(local_dir):
        for filename in files:
            local_path = os.path.join(root, filename)
            rel_path = os.path.relpath(local_path, local_dir)
            # R2 key 使用正斜杠，避免前缀为空时产生多余的斜杠
            clean_prefix = remote_prefix.strip('/')
            rel_key = rel_path.replace(os.sep, '/')
            remote_key = f"{clean_prefix}/{rel_key}" if clean_prefix else rel_key
            url = upload_file(local_path, remote_key)
            if url:
                urls.append(url)

    return urls


def list_objects(prefix: str = "") -> list:
    """列出 bucket 中的对象"""
    client = get_r2_client()

    try:
        response = client.list_objects_v2(
            Bucket=R2_BUCKET_NAME,
            Prefix=prefix,
        )
    except ClientError as e:
        print(f"[ERROR] {e}")
        return []

    objects = response.get("Contents", [])
    if not objects:
        print("(empty)")
        return []

    print(f"{'Key':<55} {'Size':>10}  {'Last Modified'}")
    print("-" * 90)
    for obj in objects:
        key = obj["Key"]
        size = obj["Size"]
        mtime = obj["LastModified"].strftime("%Y-%m-%d %H:%M")
        print(f"{key:<55} {size:>10,}  {mtime}")

    total = sum(o["Size"] for o in objects)
    print(f"\n共 {len(objects)} 个文件, 总计 {total:,} bytes")
    return objects


def test_connection():
    """测试 R2 连接"""
    print("=== Testing R2 Connection ===")
    print(f"  Account ID:    {R2_ACCOUNT_ID[:8]}..." if R2_ACCOUNT_ID else "  Account ID:    (missing)")
    print(f"  Access Key ID: {R2_ACCESS_KEY_ID[:8]}..." if R2_ACCESS_KEY_ID else "  Access Key ID: (missing)")
    print(f"  Bucket:        {R2_BUCKET_NAME}")
    print()

    try:
        client = get_r2_client()
    except SystemExit:
        return False

    try:
        # 尝试列出 bucket 中的对象（最多返回 1 个）
        response = client.list_objects_v2(
            Bucket=R2_BUCKET_NAME,
            MaxKeys=1,
        )
        print("[OK] Connection successful!")
        print(f"  Bucket '{R2_BUCKET_NAME}' is accessible.")
        count = response.get("KeyCount", 0)
        print(f"  Objects in bucket: {'>= 1' if count else '0 (empty)'}")
        return True

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code == "NoSuchBucket":
            print(f"[FAIL] Bucket '{R2_BUCKET_NAME}' 不存在")
            print("  请在 Cloudflare Dashboard 创建该 bucket")
        elif error_code == "AccessDenied":
            print("[FAIL] 访问被拒绝，请检查 API Token 权限")
        else:
            print(f"[FAIL] {e}")
        return False
    except NoCredentialsError:
        print("[FAIL] 凭据无效")
        return False
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


# ==================== CLI ====================

def delete_object(remote_key: str) -> bool:
    """删除 R2 中的单个对象

    Args:
        remote_key: R2 中的对象 key

    Returns:
        是否删除成功
    """
    client = get_r2_client()
    try:
        client.delete_object(Bucket=R2_BUCKET_NAME, Key=remote_key)
        print(f"  [OK] Deleted: {remote_key}")
        return True
    except ClientError as e:
        print(f"  [FAIL] {e}")
        return False


def delete_prefix(prefix: str) -> int:
    """删除匹配前缀的所有对象

    Args:
        prefix: R2 前缀（如 research/daily/）

    Returns:
        删除的文件数
    """
    client = get_r2_client()
    clean_prefix = prefix.strip('/')

    try:
        response = client.list_objects_v2(
            Bucket=R2_BUCKET_NAME,
            Prefix=clean_prefix,
        )
    except ClientError as e:
        print(f"[ERROR] {e}")
        return 0

    objects = response.get("Contents", [])
    if not objects:
        print(f"  No objects matching prefix: {clean_prefix}")
        return 0

    count = 0
    for obj in objects:
        if delete_object(obj["Key"]):
            count += 1
    return count


def print_usage():
    print("""
CyAnalyst R2 Upload Tool
========================

Usage:
  python upload_to_r2.py <local_file> <remote_key>
      Upload a single file

  python upload_to_r2.py --dir <local_dir> <remote_prefix>
      Upload all files in a directory recursively

  python upload_to_r2.py --list [prefix]
      List objects in the bucket

  python upload_to_r2.py --delete <remote_key>
      Delete a single object from R2

  python upload_to_r2.py --delete-prefix <prefix>
      Delete all objects matching a prefix

  python upload_to_r2.py --test
      Test R2 connection

Environment Variables (or .env file):
  R2_ACCOUNT_ID         Cloudflare Account ID
  R2_ACCESS_KEY_ID      R2 Access Key ID
  R2_SECRET_ACCESS_KEY  R2 Secret Access Key
  R2_BUCKET_NAME        Bucket name (default: cyanalyst-reports)
  R2_PUBLIC_URL         Public base URL (e.g. https://pub-xxxx.r2.dev)

Examples:
  python upload_to_r2.py scripts/output/2026-06-24-morning.html research/daily/2026-06-24-morning.html
  python upload_to_r2.py --dir scripts/output research/
  python upload_to_r2.py --list research/
  python upload_to_r2.py --delete research/daily/2026-06-24-morning.docx
  python upload_to_r2.py --delete-prefix research/daily/
  python upload_to_r2.py --test
""")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print_usage()
        sys.exit(0)

    if args[0] == "--test":
        ok = test_connection()
        sys.exit(0 if ok else 1)

    elif args[0] == "--list":
        prefix = args[1] if len(args) > 1 else ""
        list_objects(prefix)

    elif args[0] == "--delete":
        if len(args) < 2:
            print("Usage: python upload_to_r2.py --delete <remote_key>")
            sys.exit(1)
        print(f"=== Deleting: {args[1]} ===")
        delete_object(args[1])

    elif args[0] == "--delete-prefix":
        if len(args) < 2:
            print("Usage: python upload_to_r2.py --delete-prefix <prefix>")
            sys.exit(1)
        print(f"=== Deleting all objects with prefix: {args[1]} ===")
        count = delete_prefix(args[1])
        print(f"\nDone. {count} file(s) deleted.")

    elif args[0] == "--dir":
        if len(args) < 3:
            print("Usage: python upload_to_r2.py --dir <local_dir> <remote_prefix>")
            sys.exit(1)
        local_dir = args[1]
        remote_prefix = args[2]
        print(f"=== Uploading directory: {local_dir} -> {remote_prefix} ===")
        urls = upload_directory(local_dir, remote_prefix)
        print(f"\nDone. {len(urls)} file(s) uploaded.")

    else:
        if len(args) < 2:
            print("Usage: python upload_to_r2.py <local_file> <remote_key>")
            sys.exit(1)
        local_path = args[0]
        remote_key = args[1]
        print(f"=== Uploading file: {local_path} -> {remote_key} ===")
        url = upload_file(local_path, remote_key)
        if not url:
            sys.exit(1)
