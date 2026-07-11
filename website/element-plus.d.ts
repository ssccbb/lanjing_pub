import { ElIcon, ElSkeleton, ElSkeletonItem, ElPagination } from 'element-plus'

declare module 'vue' {
  export interface GlobalComponents {
    ElIcon: typeof ElIcon
    ElSkeleton: typeof ElSkeleton
    ElSkeletonItem: typeof ElSkeletonItem
    ElPagination: typeof ElPagination
  }
}

export {}
