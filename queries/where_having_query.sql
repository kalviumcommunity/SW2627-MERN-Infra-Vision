SELECT
    Branch,
    COUNT(*) AS total_students,
    AVG(Marks) AS average_marks
FROM students_cleaned
WHERE Hosteller = 1
GROUP BY Branch
HAVING AVG(Marks) > 80;