SELECT
Hosteller,
COUNT(*) AS total_students
FROM students_cleaned
GROUP BY Hosteller;