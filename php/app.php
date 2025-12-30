<?php
// Fungsi untuk membuka koneksi ke database SQLite3
function connectDB() {
    // Membuka koneksi ke database SQLite
    $db = new SQLite3('students.db'); // Ganti dengan path yang sesuai
    
    if (!$db) {
        echo "Koneksi gagal";
        return null;
    }
    return $db;
}

function selectStudentsById($id) {
    // Memanggil fungsi koneksi
    $db = connectDB();
    
    if ($db) {
        // Query untuk mengambil semua data dari tabel students
        $query = "SELECT * FROM student WHERE id=".$id;

        // Menjalankan query dan mendapatkan hasilnya
        $result = $db->query($query);

        if (!$result) {
            echo "Query gagal: " . $db->lastErrorMsg();
            return null;
        }

        // Mengambil semua data dalam bentuk array asosiatif
        $students = [];
        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            $students[] = $row;
        }

        // Mengembalikan hasil query dalam bentuk array
        return $students;
    } else {
        echo "Gagal koneksi ke database.";
        return null;
    }
}
// Fungsi untuk mendapatkan data siswa dari database
function selectStudents() {
    // Memanggil fungsi koneksi
    $db = connectDB();
    
    if ($db) {
        // Query untuk mengambil semua data dari tabel students
        $query = "SELECT * FROM student";

        // Menjalankan query dan mendapatkan hasilnya
        $result = $db->query($query);

        if (!$result) {
            echo "Query gagal: " . $db->lastErrorMsg();
            return null;
        }

        // Mengambil semua data dalam bentuk array asosiatif
        $students = [];
        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            $students[] = $row;
        }

        // Mengembalikan hasil query dalam bentuk array
        return $students;
    } else {
        echo "Gagal koneksi ke database.";
        return null;
    }
}
// Fungsi untuk menghapus data siswa berdasarkan ID
function deleteStudent($id) {
    // echo "hasil";
    $db = connectDB();
    if ($db) {
        $query = "DELETE from student where id =".$id;
        // Menjalankan query untuk menambahkan data siswa
        $result = $db->exec($query);

        if (!$result) {
            echo "Query gagal: " . $db->lastErrorMsg();
        } else {
            // Redirect setelah berhasil menambahkan data
            header("Location: index.php");
            exit;
        }
    }else{
        echo "Gagal koneksi ke database.";
    }
}
// Fungsi untuk menambahkan data siswa
function addStudent($name, $age, $grade) {
    $db = connectDB();
    if ($db) {
        // Kode ini rentan terhadap SQL Injection karena tidak ada sanitasi input
        // validasi
        $name = trim($name);
        $age = intval($age);
        $grade = trim($grade);

        $allowGrades = ['A', 'B', 'C', 'D', 'E'];
        if (!in_array($grade, $allowGrades, true)) {
            echo "Grade tidak valid.";
            return;
        }

        $stmt = $db->prepare("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)");
        $stmt->bindvalue(':name', $name, SQLITE3_TEXT);
        $stmt->bindvalue(':age', $age, SQLITE3_INTEGER);
        $stmt->bindvalue(':grade', $grade, SQLITE3_TEXT);

        // Menyusun query untuk menambahkan data siswa tanpa sanitasi input
        // $query = "INSERT INTO student (name, age, grade) VALUES ('$name', '$age', '$grade')";
        //$query = "DELETE from student where age != 999999";
        // Menjalankan query untuk menambahkan data siswa
        // $result = $db->exec($query);

        $result = $stmt->execute();
        if (!$result) {
            echo "Query gagal: " . $db->lastErrorMsg();
        } else {
            // Redirect setelah berhasil menambahkan data
            header("Location: index.php");
            exit;
        }
    } else {
        echo "Gagal koneksi ke database.";
    }
}
function updateStudent($id, $name, $age, $grade) {
    $db = connectDB();
    if ($db) {
        // Menyusun query untuk menambahkan data siswa tanpa sanitasi input
        // validasi
        $id = intval($id);
        $age = intval($age);
        $grade = trim($grade);

        // whitelist untuk grade (contoh)
        $allowGrades = ['A', 'B', 'C', 'D', 'E'];
        if ($id < 0 || !in_array($grade,  $allowGrades, true)) {
            echo "Input tidak valid.";
            return;
        }

        // $stmt = $db->prepare("UPDATE student SET name = :name, age = :age, grade = :grade WHERE id= :id");
        // $stmt->bindValue(' :name', $name, SQLITE3_TEXT);
        // $stmt->bindValue(' :age', $age, SQLITE3_INTEGER);
        // $stmt->bindValue(' :grade', $grade, SQLITE3_TEXT);
        // $stmt->bindValue(' :id', $id, SQLITE3_INTEGER);

        $query = "UPDATE student SET name = '$name', age = '$age', grade = '$grade' WHERE id=$id";
        // Menjalankan query untuk menambahkan data siswa
        $result = $db->exec($query);

        // $result = $stmt->execute();
        if (!$result) {
            echo "Query gagal: " . $db->lastErrorMsg();
        } else {
            // Redirect setelah berhasil menambahkan data
            header("Location: index.php");
            exit;
        }
    } else {
        echo "Gagal koneksi ke database.";
    }
}
