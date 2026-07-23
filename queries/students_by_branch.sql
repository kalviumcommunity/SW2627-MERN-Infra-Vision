SELECT
Branch,
COUNT(*) AS total_students,
AVG(Marks) AS average_marks
FROM students_cleaned
GROUP BY Branch;