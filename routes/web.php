<?php

declare(strict_types=1);

use App\View;

return [
    'GET /' => static function (): void {
        http_response_code(200);

        echo View::render('layout', [
            'title' => 'adelina-site',
            'content' => View::render('pages/home'),
        ]);
    },
];
