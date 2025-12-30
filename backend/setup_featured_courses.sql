-- 设置精选科创课程的 SQL 脚本
-- 使用方法: psql -d inspireed -f setup_featured_courses.sql

-- 查看现有课程
SELECT id, name, subject_id, is_featured, category 
FROM courses 
WHERE is_active = true 
LIMIT 10;

-- 示例：设置课程为精选课程（请根据实际课程ID修改）
-- 人工智能类课程
-- UPDATE courses SET is_featured = true, category = '人工智能' WHERE id = <course_id>;

-- 无人机类课程
-- UPDATE courses SET is_featured = true, category = '无人机' WHERE id = <course_id>;

-- 轮式机器人类课程
-- UPDATE courses SET is_featured = true, category = '轮式机器人' WHERE id = <course_id>;

-- 开源硬件类课程
-- UPDATE courses SET is_featured = true, category = '开源硬件' WHERE id = <course_id>;

-- 虚拟仿真类课程
-- UPDATE courses SET is_featured = true, category = '虚拟仿真' WHERE id = <course_id>;

-- 3D打印类课程
-- UPDATE courses SET is_featured = true, category = '3D打印' WHERE id = <course_id>;

-- 查看设置后的精选课程
SELECT 
    c.id,
    c.name,
    s.name as subject_name,
    g.name as grade_name,
    c.is_featured,
    c.category
FROM courses c
LEFT JOIN subjects s ON c.subject_id = s.id
LEFT JOIN grades g ON c.grade_id = g.id
WHERE c.is_featured = true
ORDER BY c.category, c.display_order;

