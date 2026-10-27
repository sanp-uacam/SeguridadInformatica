# Pruebas del login (normal + inyeccion SQL)
# Uso:
#   .\probar-login.ps1 3000      -> prueba la version VULNERABLE (/login-vulnerable)
#   .\probar-login.ps1 3001      -> prueba la version SEGURA     (/login-seguro)
#
# Requiere tener el servidor correspondiente corriendo en otra terminal:
#   node server-vulnerable.js    (puerto 3000)
#   node server-seguro.js        (puerto 3001)

param([int]$Port = 3000)

if ($Port -eq 3001) { $Endpoint = "login-seguro" } else { $Endpoint = "login-vulnerable" }
$url = "http://localhost:$Port/$Endpoint"

Write-Host ""
Write-Host "==================================================================" -ForegroundColor DarkGray
Write-Host "  Pruebas contra  $url" -ForegroundColor White
Write-Host "==================================================================" -ForegroundColor DarkGray

function Probar($titulo, $usuario, $contrasena) {
    $json  = @{ username = $usuario; password = $contrasena } | ConvertTo-Json -Compress
    $shown = '{"username":"' + $usuario + '","password":"' + $contrasena + '"}'
    Write-Host ""
    Write-Host "# $titulo" -ForegroundColor Cyan
    Write-Host "  usuario:   $usuario" -ForegroundColor DarkGray
    Write-Host "  enviado:   $shown" -ForegroundColor DarkGray
    try {
        $resp = Invoke-RestMethod -Uri $url -Method Post -ContentType "application/json" -Body $json
        Write-Host "  respuesta: $($resp | ConvertTo-Json -Compress)" -ForegroundColor Green
    } catch {
        $msg = $_.ErrorDetails.Message
        if (-not $msg) {
            try {
                $s = $_.Exception.Response.GetResponseStream()
                $msg = (New-Object System.IO.StreamReader($s)).ReadToEnd()
            } catch { $msg = $_.Exception.Message }
        }
        Write-Host "  respuesta: $msg" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "----- Login legitimo -----" -ForegroundColor Yellow
Probar "admin / admin"      "admin" "admin"
Probar "juan / 1234"        "juan"  "1234"
Probar "admin / incorrecta" "admin" "incorrecta"

Write-Host ""
Write-Host "----- Inyeccion SQL (payload en el campo usuario) -----" -ForegroundColor Yellow
Probar "PAYLOAD 1:  admin' --"       "admin' --"        "loquesea"
Probar "PAYLOAD 2:  ' OR '1'='1' --" "' OR '1'='1' --"  "loquesea"

Write-Host ""
Write-Host "==================================================================" -ForegroundColor DarkGray
Write-Host ""
