<?php
// login_seguro.php / login.php - Versión segura con Consultas Parametrizadas (Prepared Statements PDO)
session_start();

try {
    $pdo = new PDO("mysql:host=localhost;dbname=seguridad_db;charset=utf8mb4", "root", "", [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false // Desactiva emulación para separación real de código y datos
    ]);
} catch (PDOException $e) {
    die("Error de conexión a la base de datos.");
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = trim($_POST['username']);
    $password = $_POST['password'];

    // SOLUCIÓN SEGURA: Uso de marcadores de posición (?) y declaraciones preparadas
    $sql = "SELECT id, username, password_hash, role FROM users WHERE username = ?";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$username]);
    $user = $stmt->fetch();

    if ($user && password_verify($password, $user['password_hash'])) {
        session_regenerate_id(true);
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['role'] = $user['role'];
        echo "<div style='color:green; font-weight:bold;'>[+] ¡Autenticación segura exitosa! Bienvenido " . htmlspecialchars($user['username']) . "</div>";
    } else {
        echo "<div style='color:red;'>[-] Credenciales incorrectas.</div>";
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Login Seguro - Parametrizado</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="bg-light d-flex justify-content-center align-items-center vh-100">
    <div class="card p-4 shadow-sm" style="width: 400px;">
        <h3 class="card-title text-center mb-3">Iniciar Sesión (Seguro)</h3>
        <form method="POST" action="">
            <div class="mb-3">
                <label class="form-label">Usuario</label>
                <input type="text" name="username" class="form-control" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Contraseña</label>
                <input type="password" name="password" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-success w-100">Ingresar Seguro</button>
        </form>
    </div>
</body>
</html>
