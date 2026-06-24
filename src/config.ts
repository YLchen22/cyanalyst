// CyAnalyst — 站点常量配置
// R2 公共访问地址（从 .env 的 R2_PUBLIC_URL 同步）
export const R2_BASE_URL = 'https://pub-e042cb137f3f4d9d91009d7a9233dd5b.r2.dev';

/**
 * 构建 R2 研报文件 URL
 * @param category - 'daily' | 'weekly' | 'special'
 * @param id       - 研报 ID（不含扩展名）
 * @param ext      - 文件扩展名，默认 'html'
 */
export function r2Url(category: string, id: string, ext: string = 'html'): string {
  return `${R2_BASE_URL}/research/${category}/${id}.${ext}`;
}
