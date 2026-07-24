SELECT
    s.Name,
    s.Branch,
    b.HOD,
    b.Building,
    s.Marks
FROM students_cleaned s
INNER JOIN branches b
ON s.Branch = b.Branch;