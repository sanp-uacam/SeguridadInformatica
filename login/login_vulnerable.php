<?php
// login_vulnerable.php - Código vulnerable a SQL Injection en autenticación
session_start();

$conn = new mysqli("localhost", "root", "", "seguridad_db");

if ($conn->connect_error) {
    die("Error de conexión: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $_POST['username'];
    $password = $_POST['password'];

    // VULNERABILIDAD CRÍTICA: Concatenación directa de variables en la consulta SQL
    $sql = "SELECT id, username, role FROM users WHERE username = '$username' AND password = '$password'";
    
    $result = $conn->query($sql);

    if ($result && $result->num_rows > 0) {
        $user = $result->fetch_assoc();
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['role'] = $user['role'];
        echo "<div style='color:green; font-weight:bold;'>[+] ¡Autenticación exitosa! Bienvenido " . htmlspecialchars($user['username']) . " (" . $user['role'] . ")</div>";
    } else {
        echo "<div style='color:red;'>[-] Credenciales inválidas o error en la consulta.</div>";
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Login Vulnerable - SQLi Demo</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="bg-light d-flex justify-content-center align-items-center vh-100">
    <div class="card p-4 shadow-sm" style="width: 400px;">
        <h3 class="card-title text-center mb-3">Iniciar Sesión (Vulnerable)</h3>
        <form method="POST" action="">
            <div class="mb-3">
                <label class="form-label">Usuario</label>
                <input type="text" name="username" class="form-control" placeholder="admin' -- " required>
            </div>
            <div class="mb-3">
                <label class="form-label">Contraseña</label>
                <input type="password" name="password" class="form-control" placeholder="****">
            </div>
            <button type="submit" class="btn btn-danger w-100">Ingresar</button>
        </form>
    </div>
</body>
</html>
