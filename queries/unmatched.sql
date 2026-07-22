SELECT
    b.Branch,
    b.HOD
FROM branches b
LEFT JOIN students_cleaned s
ON b.Branch = s.Branch
WHERE s.Name IS NULL;