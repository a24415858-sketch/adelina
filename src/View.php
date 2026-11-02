<?php

declare(strict_types=1);

namespace App;

final class View
{
    /** @param array<string, mixed> $data */
    public static function render(string $template, array $data = []): string
    {
        $templatePath = BASE_PATH . '/templates/' . $template . '.php';

        if (!is_file($templatePath)) {
            throw new \RuntimeException('Template not found: ' . $template);
        }

        extract($data, EXTR_SKIP);

        ob_start();

        try {
            require $templatePath;

            return (string) ob_get_clean();
        } catch (\Throwable $exception) {
            ob_end_clean();

            throw $exception;
        }
    }

    public static function e(?string $value): string
    {
        return htmlspecialchars($value ?? '', ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    }
}
