SELECT
    s.Name,
    s.Branch,
    b.HOD,
    b.Building
FROM students_cleaned s
LEFT JOIN branches b
ON s.Branch = b.Branch

UNION

SELECT
    s.Name,
    b.Branch,
    b.HOD,
    b.Building
FROM branches b
LEFT JOIN students_cleaned s
ON s.Branch = b.Branch;