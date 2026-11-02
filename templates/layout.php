<?php

declare(strict_types=1);

/** @var string $title */
/** @var string $content */
?>
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?= \App\View::e($title) ?></title>
    <!-- Подключение CSS и JS появится вместе с оформлением. -->
</head>
<body>
<?= $content ?>
</body>
</html>
