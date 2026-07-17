/**
 * 收藏功能 API 接口
 * 对应后端：/api/v1/favorites
 */
import { api } from './client'

export type FavoriteTargetType = 'study_material' | 'mistake' | 'exercise'

export interface FavoriteCreateRequest {
  target_type: FavoriteTargetType
  target_id: string
}

export interface FavoriteItem {
  id: number
  user_id: string
  target_type: FavoriteTargetType
  target_id: string
  created_at: string
}

export interface FavoriteListResponse {
  total: number
  items: FavoriteItem[]
}

export interface FavoriteListParams {
  target_type?: FavoriteTargetType
  page?: number
  page_size?: number
}

/** 添加收藏 */
export const createFavorite = async (data: FavoriteCreateRequest): Promise<FavoriteItem> => {
  const response = await api.post('/favorites', data)
  return response.data
}

/** 查询收藏列表 */
export const getFavorites = async (params?: FavoriteListParams): Promise<FavoriteListResponse> => {
  const response = await api.get('/favorites', { params })
  return response.data
}

/** 取消收藏（通过收藏ID） */
export const deleteFavorite = async (favoriteId: number): Promise<void> => {
  await api.delete(`/favorites/${favoriteId}`)
}

/** 检查是否已收藏 */
export const checkFavorite = async (
  target_type: FavoriteTargetType,
  target_id: string
): Promise<{ is_favorited: boolean }> => {
  const response = await api.get('/favorites/check', { params: { target_type, target_id } })
  return response.data
}

/** 取消收藏（通过目标类型和目标ID） */
export const removeFavoriteByTarget = async (
  target_type: FavoriteTargetType,
  target_id: string
): Promise<void> => {
  const res = await getFavorites({ target_type, page_size: 100 })
  const item = res.items.find(i => i.target_id === target_id)
  if (item) {
    await deleteFavorite(item.id)
  }
}
