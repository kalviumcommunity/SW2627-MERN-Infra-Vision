SELECT
    Branch,
    AVG(Marks) AS average_marks
FROM students_cleaned
GROUP BY Branch
HAVING AVG(Marks) > 85;