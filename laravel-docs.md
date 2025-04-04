# Flalingo Laravel + React Frontend Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Project Structure](#project-structure)
5. [Configuration](#configuration)
6. [API Integration](#api-integration)
7. [Frontend Components](#frontend-components)
8. [Database Setup](#database-setup)
9. [Authentication](#authentication)
10. [Testing](#testing)
11. [Deployment](#deployment)
12. [Troubleshooting](#troubleshooting)

## Project Overview
Flalingo is a language learning platform that analyzes transcripts and generates personalized tests. This documentation covers the Laravel + React frontend that integrates with the Flask backend API.

## Prerequisites
- PHP >= 8.1
- Node.js >= 16.x
- Composer
- MySQL >= 8.0
- Laravel CLI
- Git

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd flalingo-frontend
```

### 2. Install PHP Dependencies
```bash
composer install
```

### 3. Install Node Dependencies
```bash
npm install
```

### 4. Environment Setup
```bash
cp .env.example .env
php artisan key:generate
```

Edit `.env` file with your configurations:
```env
APP_NAME=Flalingo
APP_ENV=local
APP_DEBUG=true
APP_URL=http://localhost:8000

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=flalingo
DB_USERNAME=root
DB_PASSWORD=

FLASK_API_URL=http://127.0.0.1:5000
```

### 5. Database Setup
```bash
php artisan migrate
```

### 6. Start Development Servers
```bash
# Terminal 1 - Laravel Server
php artisan serve

# Terminal 2 - Vite Development Server
npm run dev
```

## Project Structure

### Key Directories and Files
```
flalingo-frontend/
├── app/
│   ├── Http/
│   │   ├── Controllers/
│   │   │   └── TranscriptController.php
│   │   └── Middleware/
│   ├── Services/
│   │   └── FlaskApiService.php
│   └── Models/
├── resources/
│   ├── js/
│   │   ├── Components/
│   │   │   ├── TranscriptUpload.jsx
│   │   │   ├── AnalysisResults.jsx
│   │   │   └── TestQuestions.jsx
│   │   ├── Pages/
│   │   │   └── TranscriptAnalysis.jsx
│   │   └── app.jsx
│   └── views/
├── routes/
│   ├── api.php
│   └── web.php
└── config/
```

## Configuration

### 1. Laravel Configuration
Update `config/cors.php`:
```php
return [
    'paths' => ['api/*'],
    'allowed_methods' => ['*'],
    'allowed_origins' => ['http://localhost:3000'],
    'allowed_origins_patterns' => [],
    'allowed_headers' => ['*'],
    'exposed_headers' => [],
    'max_age' => 0,
    'supports_credentials' => true,
];
```

### 2. Vite Configuration
Update `vite.config.js`:
```javascript
import { defineConfig } from 'vite';
import laravel from 'laravel-vite-plugin';
import react from '@vitejs/plugin-react';

export default defineConfig({
    plugins: [
        laravel({
            input: ['resources/js/app.jsx'],
            refresh: true,
        }),
        react(),
    ],
});
```

## API Integration

### 1. Create Flask API Service
Create `app/Services/FlaskApiService.php`:
```php
namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Http\UploadedFile;

class FlaskApiService
{
    protected $baseUrl;

    public function __construct()
    {
        $this->baseUrl = env('FLASK_API_URL', 'http://127.0.0.1:5000');
    }

    public function uploadTranscript(UploadedFile $file)
    {
        try {
            $response = Http::attach(
                'transcript_file',
                file_get_contents($file->path()),
                $file->getClientOriginalName()
            )->post("{$this->baseUrl}/api/upload");

            return $response->json();
        } catch (\Exception $e) {
            return [
                'success' => false,
                'error' => 'Failed to communicate with analysis service'
            ];
        }
    }

    public function healthCheck()
    {
        try {
            return Http::get("{$this->baseUrl}/api/health")->json();
        } catch (\Exception $e) {
            return ['status' => 'error'];
        }
    }
}
```

### 2. Register Service Provider
Create `app/Providers/FlaskApiServiceProvider.php`:
```php
namespace App\Providers;

use App\Services\FlaskApiService;
use Illuminate\Support\ServiceProvider;

class FlaskApiServiceProvider extends ServiceProvider
{
    public function register()
    {
        $this->app->singleton(FlaskApiService::class, function ($app) {
            return new FlaskApiService();
        });
    }
}
```

Add to `config/app.php`:
```php
'providers' => [
    // ...
    App\Providers\FlaskApiServiceProvider::class,
],
```

## Frontend Components

### 1. Install Required Packages
```bash
npm install @headlessui/react @heroicons/react axios
```

### 2. Component Implementation
See the React components section in the previous response for detailed implementation.

### 3. State Management
For larger applications, consider using Redux or Zustand:
```bash
npm install @reduxjs/toolkit react-redux
```

## Database Setup

### 1. Create Migrations
```bash
php artisan make:migration create_transcripts_table
```

Edit the migration file:
```php
public function up()
{
    Schema::create('transcripts', function (Blueprint $table) {
        $table->id();
        $table->string('filename');
        $table->json('analysis_result')->nullable();
        $table->json('tests')->nullable();
        $table->string('file_type');
        $table->timestamps();
    });
}
```

### 2. Create Model
```bash
php artisan make:model Transcript
```

Edit `app/Models/Transcript.php`:
```php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Transcript extends Model
{
    protected $fillable = [
        'filename',
        'analysis_result',
        'tests',
        'file_type'
    ];

    protected $casts = [
        'analysis_result' => 'array',
        'tests' => 'array'
    ];
}
```

## Authentication

### 1. Install Laravel Breeze
```bash
composer require laravel/breeze --dev
php artisan breeze:install react
```

### 2. Configure Authentication
Update `routes/auth.php` as needed.

## Testing

### 1. Unit Tests
Create `tests/Unit/FlaskApiServiceTest.php`:
```php
namespace Tests\Unit;

use Tests\TestCase;
use App\Services\FlaskApiService;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Http;

class FlaskApiServiceTest extends TestCase
{
    public function test_upload_transcript()
    {
        Http::fake([
            '*/api/upload' => Http::response([
                'success' => true,
                'data' => [
                    'analysis' => '...',
                    'tests' => [],
                    'file_type' => 'txt'
                ]
            ], 200)
        ]);

        $service = new FlaskApiService();
        $file = UploadedFile::fake()->create('test.txt', 100);
        
        $response = $service->uploadTranscript($file);
        
        $this->assertTrue($response['success']);
    }
}
```

### 2. Feature Tests
Create `tests/Feature/TranscriptControllerTest.php`:
```php
namespace Tests\Feature;

use Tests\TestCase;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;

class TranscriptControllerTest extends TestCase
{
    public function test_upload_transcript()
    {
        Storage::fake('local');

        $file = UploadedFile::fake()->create('transcript.txt', 100);

        $response = $this->post('/api/transcript/upload', [
            'transcript_file' => $file
        ]);

        $response->assertStatus(200);
    }
}
```

## Deployment

### 1. Production Environment
Update `.env.production`:
```env
APP_ENV=production
APP_DEBUG=false
FLASK_API_URL=https://api.your-domain.com
```

### 2. Build Assets
```bash
npm run build
```

### 3. Server Configuration
Example Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/flalingo-frontend/public;

    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";

    index index.php;

    charset utf-8;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt  { access_log off; log_not_found off; }

    error_page 404 /index.php;

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }
}
```

### 4. SSL Configuration
```bash
sudo certbot --nginx -d your-domain.com
```

## Troubleshooting

### Common Issues and Solutions

1. **CORS Issues**
```php
// config/cors.php
return [
    'paths' => ['api/*'],
    'allowed_origins' => ['*'],
    // ...
];
```

2. **File Upload Issues**
Check `php.ini` settings:
```ini
upload_max_filesize = 20M
post_max_size = 20M
```

3. **API Connection Issues**
- Verify FLASK_API_URL in .env
- Check network connectivity
- Verify Flask API is running

### Debug Tools
1. Laravel Telescope installation:
```bash
composer require laravel/telescope --dev
php artisan telescope:install
php artisan migrate
```

2. React Developer Tools:
```bash
npm install -D @redux-devtools/extension
```

## Security Considerations

1. **File Upload Security**
```php
// config/filesystems.php
'uploads' => [
    'driver' => 'local',
    'root' => storage_path('app/uploads'),
    'permissions' => [
        'file' => [
            'public' => 0644,
            'private' => 0600,
        ],
        'dir' => [
            'public' => 0755,
            'private' => 0700,
        ],
    ],
],
```

2. **API Security**
```php
// app/Http/Middleware/VerifyApiToken.php
namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class VerifyApiToken
{
    public function handle(Request $request, Closure $next)
    {
        if ($request->header('X-API-Token') !== config('services.flask.token')) {
            return response()->json(['error' => 'Unauthorized'], 401);
        }

        return $next($request);
    }
}
```

## Maintenance

### Regular Tasks
1. Update dependencies:
```bash
composer update
npm update
```

2. Clear cache:
```bash
php artisan cache:clear
php artisan config:clear
php artisan route:clear
php artisan view:clear
```

3. Monitor logs:
```bash
tail -f storage/logs/laravel.log
```

### Backup Strategy
1. Database backup:
```bash
php artisan backup:run
```

2. File backup:
```bash
# Add to crontab
0 0 * * * tar -czf /backup/flalingo-$(date +\%Y\%m\%d).tar.gz /var/www/flalingo-frontend
``` 