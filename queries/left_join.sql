SELECT
    s.Name,
    s.Branch,
    b.HOD,
    b.Building
FROM students_cleaned s
LEFT JOIN branches b
ON s.Branch = b.Branch;