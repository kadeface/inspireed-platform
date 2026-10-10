/** 授课进度：当前展示模块在整课中的位置，而不是同时勾选的个数。 */

export function classroomDisplayProgress(
  cells: Array<{ order?: number }>,
  displayOrders: number[],
): number {
  if (!cells.length || !displayOrders.length) return 0

  const indices = displayOrders
    .map((order) =>
      cells.findIndex((cell, index) => (cell.order !== undefined ? cell.order : index) === order),
    )
    .filter((index) => index >= 0)

  if (!indices.length) return 0
  const furthest = Math.max(...indices)
  return Math.round(((furthest + 1) / cells.length) * 100)
}
