<?php

declare(strict_types=1);

namespace App;

final class Router
{
    /** @param array<string, callable> $routes */
    public function __construct(private readonly array $routes)
    {
    }

    public function dispatch(string $method, string $path): void
    {
        $path = '/' . trim($path, '/');
        $key = strtoupper($method) . ' ' . $path;

        if (!isset($this->routes[$key])) {
            $this->notFound();

            return;
        }

        ($this->routes[$key])();
    }

    private function notFound(): void
    {
        http_response_code(404);

        echo View::render('layout', [
            'title' => '404',
            'content' => View::render('pages/404'),
        ]);
    }
}
