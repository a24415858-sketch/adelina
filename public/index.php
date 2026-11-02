<?php

declare(strict_types=1);

$uri = rawurldecode(parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/');
$publicRoot = realpath(__DIR__);
$staticFile = realpath(__DIR__ . $uri);

// Встроенный PHP-сервер отдаёт статику сам, когда router возвращает false.
if (
    $uri !== '/'
    && $staticFile !== false
    && $publicRoot !== false
    && str_starts_with($staticFile, $publicRoot . DIRECTORY_SEPARATOR)
    && !str_ends_with($staticFile, '.php')
    && is_file($staticFile)
) {
    return false;
}

require dirname(__DIR__) . '/src/bootstrap.php';

/** @var array<string, callable> $routes */
$routes = require BASE_PATH . '/routes/web.php';

$router = new App\Router($routes);
$router->dispatch($_SERVER['REQUEST_METHOD'] ?? 'GET', $uri);
