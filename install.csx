#!/usr/bin/env dotnet-script
// install.csx — Claude Forge 설치 및 .NET 프로젝트 초기화 (크로스플랫폼)
//
// 사용법:
//   dotnet script install.csx                         # Claude Forge 설치
//   dotnet script install.csx -- --AppName MyApp      # .NET 프로젝트 생성
//   dotnet script install.csx -- --AppName MyApp --ParentDir D:\projects
//
// 도구 설치 (최초 1회):
//   dotnet tool install -g dotnet-script

#nullable enable
#r "nuget: System.Text.Json, 8.0.0"

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.Json;

// ──────────────────────────────────────────────
// 배너
// ──────────────────────────────────────────────
Print("");
Print("   ╔═╗┬  ┌─┐┬ ┬┌┬┐┌─┐  ╔═╗┌─┐┬─┐┌─┐┌─┐", ConsoleColor.Cyan);
Print("   ║  │  ├─┤│ │ ││├┤   ╠╣ │ │├┬┘│ ┬├┤ ", ConsoleColor.Cyan);
Print("   ╚═╝┴─┘┴ ┴└─┘─┴┘└─┘  ╚  └─┘┴└─└─┘└─┘", ConsoleColor.Cyan);
Print("                              for .NET", ConsoleColor.Blue);
Print("");
Print("   Production-grade Claude Code Framework for .NET", ConsoleColor.White);
Print("   github.com/daeha76/claude-forge",   ConsoleColor.DarkGray);
Print("");

// ──────────────────────────────────────────────
// 스크립트 위치 기준 경로 계산
// ──────────────────────────────────────────────
string repoDir = Environment.GetCommandLineArgs()
    .Where(a => a.EndsWith(".csx", StringComparison.OrdinalIgnoreCase) && File.Exists(a))
    .Select(a => Path.GetDirectoryName(Path.GetFullPath(a))!)
    .FirstOrDefault()
    ?? Directory.GetCurrentDirectory();

// ──────────────────────────────────────────────
// 인수 파싱
// 우선순위: 환경변수 (래퍼) > 직접 Args (직접 실행 시)
//
// 래퍼를 통한 사용: .\install.ps1 MyApp
// 직접 실행:    dotnet script install.csx MyApp
//                dotnet script install.csx MyApp D:\projects
// ──────────────────────────────────────────────

// 1순위: 환경변수 (래퍼 install.ps1 / install.sh이 설정)
string appName   = Environment.GetEnvironmentVariable("FORGE_APP_NAME")   ?? "";
string parentDir = Environment.GetEnvironmentVariable("FORGE_PARENT_DIR") ?? "";

// 2순위: 직접 주어진 Args (첫 번째 = 앱 이름, 두 번째 = 부모 경로)
if (string.IsNullOrEmpty(appName) && Args.Count > 0)
    appName = Args[0];
if (string.IsNullOrEmpty(parentDir) && Args.Count > 1)
    parentDir = Args[1];

// 부모 경로 기본값: claude-forge 상위 폴더
if (string.IsNullOrEmpty(parentDir))
    parentDir = Path.GetDirectoryName(repoDir) ?? Directory.GetCurrentDirectory();

string claudeDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".claude");
// ──────────────────────────────────────────────
// 플랫폼 감지
// ──────────────────────────────────────────────
bool isWindows = RuntimeInformation.IsOSPlatform(OSPlatform.Windows);
bool isMacOS   = RuntimeInformation.IsOSPlatform(OSPlatform.OSX);
bool isLinux   = RuntimeInformation.IsOSPlatform(OSPlatform.Linux);
bool isWsl     = isLinux && File.Exists("/proc/sys/fs/binfmt_misc/WSLInterop");
string platform = isWindows ? "windows" : isMacOS ? "macos" : isWsl ? "wsl" : "linux";

// WSL에서 Windows 파일시스템 경로면 심볼릭 링크 불가
bool useSymlinks = !isWindows && !(isWsl && repoDir.StartsWith("/mnt/"));

Print($"   Platform: {platform} | Symlinks: {(useSymlinks ? "yes" : "no (copy mode)")}", ConsoleColor.DarkGray);
Print("");

// ──────────────────────────────────────────────
// 분기: 모드 2 — .NET 프로젝트 초기화
// ──────────────────────────────────────────────
if (!string.IsNullOrEmpty(appName))
{
    var targetPath = Path.Combine(parentDir, appName);
    Print($"  [모드 2] .NET 프로젝트 초기화", ConsoleColor.Cyan);
    Print($"   앱 이름 : {appName}", ConsoleColor.White);
    Print($"   생성 위치: {targetPath}", ConsoleColor.White);
    Print("");
    InitDotNetProject(appName, parentDir);
    return;
}

// ──────────────────────────────────────────────
// 모드 1 — Claude Forge 설치
// ──────────────────────────────────────────────
Print("  [모드 1] Claude Forge 설치", ConsoleColor.Cyan);
Print("");

CheckDependencies();
InitSubmodules();
BackupExistingConfig();
LinkOrCopyFiles();
ApplyCcChipsOverlay();

if (VerifyInstallation())
{
    WriteForgeMetadata();
    if (!isWindows) SetupShellAliases();
    InstallMcpServers();
    InstallExternalSkills();
    InstallWorkTracker();

    Print("");
    Print("  ╔══════════════════════════════════════════════════════╗", ConsoleColor.Green);
    Print("  ║           Claude Forge for .NET 설치 완료!           ║", ConsoleColor.Green);
    Print("  ╠══════════════════════════════════════════════════════╣", ConsoleColor.Green);
    Print("  ║  11 agents · 55 commands · 12 rules · 18 skills     ║", ConsoleColor.Green);
    Print("  ╚══════════════════════════════════════════════════════╝", ConsoleColor.Green);
    Print("");
    Print("  처음이신가요? 이것만 하세요:", ConsoleColor.Cyan);
    Print("    1. 새 터미널 열고 'claude' 실행");
    Print("    2. /guide 입력 — 3분 인터랙티브 가이드");
    Print("");
    Print("  .NET 앱 프로젝트를 새로 만들려면:", ConsoleColor.DarkGray);
    Print("    dotnet script install.csx -- --AppName <앱이름>", ConsoleColor.DarkGray);
    Print("");
    Print("  ★ github.com/daeha76/claude-forge", ConsoleColor.Yellow);
}
else
{
    Print("\n  [오류] 설치 중 문제가 발생했습니다. 위 메시지를 확인하세요.", ConsoleColor.Red);
    Environment.Exit(1);
}

// ══════════════════════════════════════════════
// ▶ 모드 1 함수들
// ══════════════════════════════════════════════

void CheckDependencies()
{
    Print("필수 도구 확인 중...", ConsoleColor.White);
    var missing = new List<string>();

    if (!CommandExists("node")) missing.Add("node");
    if (!CommandExists("git"))  missing.Add("git");

    if (!CommandExists("dotnet"))
    {
        Print("  [참고] .NET SDK 미설치 — .NET 프로젝트 기능 사용 시 필요", ConsoleColor.Yellow);
        Print("         설치: https://dot.net/download", ConsoleColor.Yellow);
        Print("");
    }
    else
    {
        var ver = RunCapture("dotnet", "--version");
        Print($"  [OK] .NET SDK: {ver.Trim()}", ConsoleColor.Green);
    }

    if (missing.Count > 0)
    {
        Print($"  [오류] 미설치 도구: {string.Join(", ", missing)}", ConsoleColor.Red);
        if (isMacOS)        Print("         brew install " + string.Join(" ", missing));
        else if (!isWindows) Print("         sudo apt install " + string.Join(" ", missing));
        else                 Print("         winget install " + string.Join(" ", missing));
        Environment.Exit(1);
    }

    Print("  [OK] 모든 필수 도구 확인 완료", ConsoleColor.Green);
}

void InitSubmodules()
{
    Print("");
    Print("git 서브모듈 초기화 중...", ConsoleColor.White);
    int code = Run("git", "submodule update --init --recursive", repoDir);
    if (code == 0) Print("  [OK] cc-chips 서브모듈 초기화 완료", ConsoleColor.Green);
    else           Print("  [참고] 서브모듈 초기화 건너뜀 (이미 초기화됨)", ConsoleColor.Yellow);
}

void BackupExistingConfig()
{
    if (!Directory.Exists(claudeDir)) return;

    Print("");
    Print($"  기존 ~/.claude 폴더 발견", ConsoleColor.Yellow);
    Console.Write($"  백업할까요? (y/n): ");
    var reply = Console.ReadLine()?.Trim().ToLower();
    if (reply == "y")
    {
        var backup = $"{claudeDir}.backup.{DateTime.Now:yyyyMMdd_HHmmss}";
        Directory.Move(claudeDir, backup);
        Print($"  [OK] 백업: {backup}", ConsoleColor.Green);
    }
    else
    {
        Print("  백업 건너뜀", ConsoleColor.Yellow);
    }
}

void LinkOrCopyFiles()
{
    Print("");
    Print(useSymlinks ? "심볼릭 링크 생성 중..." : "파일 복사 중...", ConsoleColor.White);

    Directory.CreateDirectory(claudeDir);

    var dirs = new[] { "agents", "rules", "commands", "scripts", "skills", "hooks", "cc-chips", "cc-chips-custom" };
    foreach (var dir in dirs)
    {
        var src  = Path.Combine(repoDir, dir);
        var dest = Path.Combine(claudeDir, dir);
        if (!Directory.Exists(src)) continue;

        if (Directory.Exists(dest) || File.Exists(dest)) DeletePath(dest);

        if (useSymlinks) Directory.CreateSymbolicLink(dest, src);
        else             CopyDirectory(src, dest);

        Print($"  [OK] {dir}/", ConsoleColor.DarkGray);
    }

    var files = new[] { "settings.json", "hooks.json" };
    foreach (var file in files)
    {
        var src  = Path.Combine(repoDir, file);
        var dest = Path.Combine(claudeDir, file);
        if (!File.Exists(src)) continue;

        if (File.Exists(dest)) File.Delete(dest);

        if (useSymlinks) File.CreateSymbolicLink(dest, src);
        else             File.Copy(src, dest);

        Print($"  [OK] {file}", ConsoleColor.DarkGray);
    }
}

void ApplyCcChipsOverlay()
{
    var customDir = Path.Combine(repoDir, "cc-chips-custom");
    var target    = Path.Combine(claudeDir, "cc-chips");
    if (!Directory.Exists(customDir) || !Directory.Exists(target)) return;

    Print("");
    Print("CC CHIPS 커스텀 오버레이 적용 중...", ConsoleColor.White);

    var engineSrc = Path.Combine(customDir, "engine.sh");
    if (File.Exists(engineSrc))
    {
        File.Copy(engineSrc, Path.Combine(target, "engine.sh"), overwrite: true);
        Print("  [OK] engine.sh", ConsoleColor.Green);
    }

    var themesSrc = Path.Combine(customDir, "themes");
    var themesDst = Path.Combine(target, "themes");
    if (Directory.Exists(themesSrc) && Directory.Exists(themesDst))
    {
        foreach (var f in Directory.GetFiles(themesSrc, "*.sh"))
            File.Copy(f, Path.Combine(themesDst, Path.GetFileName(f)), overwrite: true);
        Print("  [OK] themes/", ConsoleColor.Green);
    }

    Print("  [OK] 오버레이 적용 완료", ConsoleColor.Green);
}

bool VerifyInstallation()
{
    Print("");
    Print("설치 확인 중...", ConsoleColor.White);
    int errors = 0;
    var items  = new[] { "agents", "rules", "commands", "skills", "cc-chips", "settings.json" };
    foreach (var item in items)
    {
        var path = Path.Combine(claudeDir, item);
        if (Directory.Exists(path) || File.Exists(path))
            Print($"  [OK] {item}", ConsoleColor.Green);
        else
        {
            Print($"  [실패] {item} — 없음", ConsoleColor.Red);
            errors++;
        }
    }
    return errors == 0;
}

void WriteForgeMetadata()
{
    Print("");
    Print("메타데이터 기록 중...", ConsoleColor.White);

    var metaPath     = Path.Combine(claudeDir, ".forge-meta.json");
    string installMode = useSymlinks ? "symlink" : "copy";
    string now        = DateTime.UtcNow.ToString("o");
    string installedAt = now;

    // 기존 installed_at 보존
    if (File.Exists(metaPath))
    {
        try
        {
            var prev = JsonDocument.Parse(File.ReadAllText(metaPath));
            if (prev.RootElement.TryGetProperty("installed_at", out var ia))
                installedAt = ia.GetString() ?? now;
        }
        catch { }
    }

    string gitCommit = RunCapture("git", "rev-parse --short HEAD", repoDir).Trim();
    string remoteUrl = RunCapture("git", "remote get-url origin", repoDir).Trim();

    var meta = new
    {
        repo_path    = repoDir,
        install_mode = installMode,
        installed_at = installedAt,
        updated_at   = now,
        git_commit   = gitCommit,
        remote_url   = remoteUrl,
        platform
    };

    File.WriteAllText(metaPath, JsonSerializer.Serialize(meta, new JsonSerializerOptions { WriteIndented = true }));
    Print("  [OK] .forge-meta.json", ConsoleColor.Green);
}

void SetupShellAliases()
{
    Print("");
    Print("셸 별칭 설정 중...", ConsoleColor.White);

    string? rcFile = null;
    string home    = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
    if (File.Exists(Path.Combine(home, ".zshrc")))  rcFile = Path.Combine(home, ".zshrc");
    else if (File.Exists(Path.Combine(home, ".bashrc"))) rcFile = Path.Combine(home, ".bashrc");

    if (rcFile is null) { Print("  [참고] .zshrc / .bashrc 없음 — 건너뜀", ConsoleColor.Yellow); return; }

    var content = File.ReadAllText(rcFile);
    if (content.Contains("# Claude Code aliases"))
    {
        Print($"  [OK] 별칭 이미 존재 ({Path.GetFileName(rcFile)})", ConsoleColor.Green);
        return;
    }

    File.AppendAllText(rcFile, "\n# Claude Code aliases\nalias cc='claude'\nalias ccr='claude --resume'\n");
    Print($"  [OK] 별칭 추가 → {Path.GetFileName(rcFile)} (cc, ccr)", ConsoleColor.Green);
}

void InstallMcpServers()
{
    Print("");
    Print("MCP 서버 설치...", ConsoleColor.White);

    if (!CommandExists("claude"))
    {
        Print("  [참고] Claude CLI 없음 — 건너뜀", ConsoleColor.Yellow);
        Print("         설치: https://claude.ai/download", ConsoleColor.Yellow);
        return;
    }

    Console.Write("  권장 MCP 서버를 설치할까요? (y/n): ");
    if (Console.ReadLine()?.Trim().ToLower() != "y") { Print("  건너뜀", ConsoleColor.DarkGray); return; }

    var core = new (string Name, string Cmd)[]
    {
        ("context7",            "claude mcp add context7 -- npx -y @upstash/context7-mcp"),
        ("playwright",          "claude mcp add playwright -- npx @playwright/mcp@latest"),
        ("memory",              "claude mcp add memory -- npx -y @modelcontextprotocol/server-memory"),
        ("sequential-thinking", "claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking"),
    };

    foreach (var (name, cmd) in core)
    {
        Print($"  {name}...");
        var parts = cmd.Split(' ', 2);
        int code  = Run(parts[0], parts[1]);
        if (code == 0) Print($"  [OK] {name}", ConsoleColor.Green);
        else           Print($"  [참고] {name} — 이미 설치 또는 실패", ConsoleColor.Yellow);
    }

    // 선택적 서버
    Print("");
    var optional = new (string Name, string Pkg)[]
    {
        ("github",    "claude mcp add github -- npx -y @modelcontextprotocol/server-github"),
        ("supabase",  "claude mcp add supabase -- npx -y @supabase/mcp-server-supabase@latest"),
    };
    foreach (var (name, cmd) in optional)
    {
        Console.Write($"  {name} 설치? (y/n): ");
        if (Console.ReadLine()?.Trim().ToLower() != "y") continue;
        var parts = cmd.Split(' ', 2);
        int code  = Run(parts[0], parts[1]);
        if (code == 0) Print($"  [OK] {name}", ConsoleColor.Green);
        else           Print($"  [참고] {name} — 실패", ConsoleColor.Yellow);
    }

    Print("  [OK] MCP 서버 설치 완료", ConsoleColor.Green);
}

void InstallExternalSkills()
{
    if (!CommandExists("npx")) return;

    Print("");
    Console.Write("  외부 스킬 설치? (Superpowers, Humanizer 등) (y/n): ");
    if (Console.ReadLine()?.Trim().ToLower() != "y") { Print("  건너뜀", ConsoleColor.DarkGray); return; }

    var skills = new (string Name, string Args)[]
    {
        ("superpowers",   "skills add obra/superpowers -y -g"),
        ("humanizer",     "skills add blader/humanizer -y -g"),
        ("ui-ux-pro-max", "skills add nextlevelbuilder/ui-ux-pro-max-skill -y -g"),
    };

    foreach (var (name, args) in skills)
    {
        Print($"  {name}...");
        int code = Run("npx", $"-y {args}");
        if (code == 0) Print($"  [OK] {name}", ConsoleColor.Green);
        else           Print($"  [참고] {name} — 실패", ConsoleColor.Yellow);
    }
}

void InstallWorkTracker()
{
    var wtScript = Path.Combine(repoDir, "setup", "work-tracker-install.sh");
    if (!File.Exists(wtScript) || isWindows) return;

    Print("");
    Console.Write("  Work Tracker 설치? (Claude Code 사용량 → Supabase) (y/n): ");
    if (Console.ReadLine()?.Trim().ToLower() != "y") return;

    Run("bash", wtScript);
}

// ══════════════════════════════════════════════
// ▶ 모드 2 — .NET 프로젝트 초기화
// ══════════════════════════════════════════════

void InitDotNetProject(string name, string baseDir)
{
    Print($"  [모드 2] .NET 프로젝트 초기화: {name}", ConsoleColor.Cyan);
    Print("");

    // 사전 확인
    if (!CommandExists("dotnet"))
    {
        Print("  [오류] .NET SDK 미설치", ConsoleColor.Red);
        Print("         설치: https://dot.net/download", ConsoleColor.Yellow);
        Environment.Exit(1);
    }
    var dotnetVer = RunCapture("dotnet", "--version").Trim();
    Print($"  [OK] .NET SDK: {dotnetVer}", ConsoleColor.Green);

    if (!CommandExists("git"))
    {
        Print("  [오류] git 미설치", ConsoleColor.Red);
        Environment.Exit(1);
    }

    // 프로젝트 루트 생성
    var root = Path.Combine(baseDir, name);
    if (Directory.Exists(root))
    {
        Print($"  [경고] 폴더가 이미 존재합니다: {root}", ConsoleColor.Yellow);
        Console.Write("  계속할까요? (y/n): ");
        if (Console.ReadLine()?.Trim().ToLower() != "y") return;
    }
    else
    {
        Directory.CreateDirectory(root);
        Print($"  [OK] 폴더 생성: {root}", ConsoleColor.Green);
    }

    Print("");
    Print("  .NET Clean Architecture 솔루션 생성 중...", ConsoleColor.White);

    // 솔루션 파일 (.slnx 포맷 — XML 기반, 머지 충돌 최소화)
    Run("dotnet", $"new sln --format slnx -n {name} --output .", root);
    Print($"  [OK] {name}.slnx", ConsoleColor.Green);

    // src 프로젝트 정의
    var srcProjects = new (string Template, string Extra, string ProjName, string Dir)[]
    {
        ("classlib", "",                                              $"{name}.Domain",         Path.Combine("src", $"{name}.Domain")),
        ("classlib", "",                                              $"{name}.Application",    Path.Combine("src", $"{name}.Application")),
        ("classlib", "",                                              $"{name}.Infrastructure", Path.Combine("src", $"{name}.Infrastructure")),
        ("webapi",   "",                                              $"{name}.Api",             Path.Combine("src", $"{name}.Api")),
        ("blazor",   "--interactivity Auto --empty",                  $"{name}.Web",             Path.Combine("src", $"{name}.Web")),
    };

    // tests 프로젝트 정의
    var testProjects = new (string Template, string Extra, string ProjName, string Dir)[]
    {
        ("xunit", "", $"{name}.Domain.Tests",      Path.Combine("tests", $"{name}.Domain.Tests")),
        ("xunit", "", $"{name}.Application.Tests", Path.Combine("tests", $"{name}.Application.Tests")),
    };

    // 생성 + 솔루션 추가
    foreach (var (tmpl, extra, proj, dir) in srcProjects.Concat(testProjects))
    {
        var fullDir = Path.Combine(root, dir);
        Directory.CreateDirectory(fullDir);
        Run("dotnet", $"new {tmpl} -n {proj} --output . --force {extra}".Trim(), fullDir);

        if (tmpl == "blazor")
        {
            // Blazor Auto 템플릿이 자동 생성한 중첩 .sln/.slnx 삭제 (루트 솔루션과 충돌 방지)
            foreach (var f in Directory.GetFiles(fullDir, "*.sln", SearchOption.AllDirectories)) File.Delete(f);
            foreach (var f in Directory.GetFiles(fullDir, "*.slnx", SearchOption.AllDirectories)) File.Delete(f);
            // Blazor Auto = 서버 프로젝트 + WASM 클라이언트 프로젝트 → 루트 솔루션에 각각 추가
            Run("dotnet", $"sln add {dir}/{proj}", root);
            Run("dotnet", $"sln add {dir}/{proj}.Client", root);
        }
        else
        {
            Run("dotnet", $"sln add {dir}", root);
        }

        // classlib 기본 빈 파일 삭제
        var class1 = Path.Combine(fullDir, "Class1.cs");
        if (File.Exists(class1)) File.Delete(class1);

        Print($"  [OK] {proj}", ConsoleColor.Green);
    }

    // Clean Architecture 참조 설정
    Print("");
    Print("  프로젝트 참조 연결 중...", ConsoleColor.White);
    // Blazor Auto는 src/{name}.Web/{name}.Web/ (서버) + src/{name}.Web/{name}.Web.Client/ (WASM) 이중 구조
    // apphost.cs는 루트에서 AddCSharpApp() 방식 사용 → Api/Web ProjectReference 불필요
    var refs = new (string From, string To)[]
    {
        ($"src/{name}.Application",                 $"src/{name}.Domain"),
        ($"src/{name}.Infrastructure",              $"src/{name}.Application"),
        ($"src/{name}.Api",                         $"src/{name}.Infrastructure"),
        ($"src/{name}.Api",                         $"src/{name}.Application"),
        ($"src/{name}.Web/{name}.Web",              $"src/{name}.Application"),
        ($"tests/{name}.Domain.Tests",              $"src/{name}.Domain"),
        ($"tests/{name}.Application.Tests",         $"src/{name}.Application"),
    };
    foreach (var (from, to) in refs)
        Run("dotnet", $"add {from} reference {to}", root);
    Print("  [OK] 참조 연결 완료", ConsoleColor.Green);

    // ── NuGet 패키지 설치 ──────────────────────────────────
    Print("");
    Print("  NuGet 패키지 설치 중...", ConsoleColor.White);

    // Infrastructure
    var infraDir = Path.Combine(root, "src", $"{name}.Infrastructure");
    var infraPackages = new[]
    {
        "Supabase",
        "Npgsql.EntityFrameworkCore.PostgreSQL",
        "Microsoft.EntityFrameworkCore.Design",
        "Microsoft.EntityFrameworkCore.Tools",
    };
    foreach (var pkg in infraPackages)
    {
        Run("dotnet", $"add package {pkg}", infraDir);
        Print($"  [OK] Infrastructure ← {pkg}", ConsoleColor.DarkGray);
    }

    // Api
    var apiDir = Path.Combine(root, "src", $"{name}.Api");
    var apiPackages = new[]
    {
        "Microsoft.AspNetCore.Authentication.JwtBearer",
        "Swashbuckle.AspNetCore",
    };
    foreach (var pkg in apiPackages)
    {
        Run("dotnet", $"add package {pkg}", apiDir);
        Print($"  [OK] Api ← {pkg}", ConsoleColor.DarkGray);
    }

    // Application
    var appDir = Path.Combine(root, "src", $"{name}.Application");
    Run("dotnet", "add package MediatR", appDir);
    Print($"  [OK] Application ← MediatR", ConsoleColor.DarkGray);
    Run("dotnet", "add package FluentValidation", appDir);
    Print($"  [OK] Application ← FluentValidation", ConsoleColor.DarkGray);

    // Tests
    var domainTestDir = Path.Combine(root, "tests", $"{name}.Domain.Tests");
    var appTestDir    = Path.Combine(root, "tests", $"{name}.Application.Tests");
    foreach (var testDir in new[] { domainTestDir, appTestDir })
    {
        Run("dotnet", "add package NSubstitute", testDir);
        Run("dotnet", "add package FluentAssertions", testDir);
    }
    Print("  [OK] Tests ← NSubstitute, FluentAssertions", ConsoleColor.DarkGray);
    Print("  [OK] NuGet 패키지 설치 완료", ConsoleColor.Green);

    // ── Bootstrap 제거 + TailwindCSS v4 설정 ──────────────────────────
    Print("");
    Print("  Bootstrap 제거 + TailwindCSS v4 설정 중...", ConsoleColor.White);

    // Blazor Auto: 실제 서버 프로젝트는 src/{name}.Web/{name}.Web/ 에 위치 (중첩 구조)
    var webServerProjectDir = Path.Combine(root, "src", $"{name}.Web", $"{name}.Web");
    var wwwrootDir   = Path.Combine(webServerProjectDir, "wwwroot");
    var cssDir       = Path.Combine(wwwrootDir, "css");
    var bootstrapDir = Path.Combine(cssDir, "bootstrap");
    if (Directory.Exists(bootstrapDir))
    {
        Directory.Delete(bootstrapDir, recursive: true);
        Print("  [OK] wwwroot/css/bootstrap/ 삭제", ConsoleColor.Green);
    }

    // app.css: Bootstrap import 제거 + Tailwind v4 @import 추가
    Directory.CreateDirectory(cssDir);
    var appCssPath = Path.Combine(cssDir, "app.css");
    var cssContent = File.Exists(appCssPath) ? File.ReadAllText(appCssPath) : "";
    cssContent = System.Text.RegularExpressions.Regex.Replace(
        cssContent, "@import\\s+[\"']bootstrap[^\"']*[\"'];?\\s*\\n?", "");
    cssContent = System.Text.RegularExpressions.Regex.Replace(
        cssContent, @"\.btn[^{]*\{[^}]*\}\s*", "");
    File.WriteAllText(appCssPath, cssContent.TrimEnd() + "\n", Encoding.UTF8);
    Print("  [OK] app.css → Bootstrap 제거 완료", ConsoleColor.Green);

    // tailwindcss_input.css: Tailwind v4 진입점 (빌드 입력 파일)
    var twInputPath = Path.Combine(cssDir, "tailwindcss_input.css");
    File.WriteAllText(twInputPath, "@import \"tailwindcss\";\n", Encoding.UTF8);
    Print("  [OK] tailwindcss_input.css 생성 (@import \"tailwindcss\")", ConsoleColor.Green);

    // App.razor: Bootstrap CDN 링크 제거 + tailwindcss_output.css 링크 추가
    var appRazorPath = Path.Combine(webServerProjectDir, "Components", "App.razor");
    if (!File.Exists(appRazorPath))
        appRazorPath = Path.Combine(webServerProjectDir, "App.razor");
    if (File.Exists(appRazorPath))
    {
        var razor = File.ReadAllText(appRazorPath);
        razor = System.Text.RegularExpressions.Regex.Replace(
            razor, @"<link[^>]*bootstrap[^>]*>\s*\n?", "",
            System.Text.RegularExpressions.RegexOptions.IgnoreCase);
        // tailwindcss_output.css 링크 추가 (Aspire watch 모드의 출력 파일)
        if (!razor.Contains("tailwindcss_output.css"))
            razor = razor.Replace("</head>", "    <link rel=\"stylesheet\" href=\"css/tailwindcss_output.css\" />\n</head>");
        File.WriteAllText(appRazorPath, razor, Encoding.UTF8);
        Print("  [OK] App.razor → Bootstrap 제거 + tailwindcss_output.css 링크 추가", ConsoleColor.Green);
    }
    Print("  [OK] Bootstrap 제거 완료", ConsoleColor.Green);

    // ── TailwindCSS v4 npm 설치 ──────────────────────────────────────
    // 공식 CLI 문서: https://tailwindcss.com/docs/installation/tailwind-cli
    Print("");
    Print("  TailwindCSS v4 npm 패키지 설치 중...", ConsoleColor.White);
    Print("  (참고: https://tailwindcss.com/docs/installation/tailwind-cli)", ConsoleColor.DarkGray);
    if (CommandExists("npm"))
    {
        Run("npm", "init -y", webServerProjectDir);
        Run("npm", "install --save-dev tailwindcss @tailwindcss/cli", webServerProjectDir);
        Print("  [OK] npm install tailwindcss @tailwindcss/cli (--save-dev)", ConsoleColor.Green);
    }
    else
    {
        Print("  [참고] npm 없음 — aspire run 시 npx로 @tailwindcss/cli 자동 다운로드됩니다", ConsoleColor.Yellow);
        Print("         권장: https://nodejs.org 설치 후 npm install 실행", ConsoleColor.Yellow);
    }
    Print("  [OK] TailwindCSS v4 설정 완료", ConsoleColor.Green);

    // ── apphost.cs 생성 (루트, file-based Aspire) ──────────────────────────────────────
    Print("");
    Print("  apphost.cs 생성 중...", ConsoleColor.White);
    // ASPIRE006: 리소스 이름에 점(.) 불허 → 하이픈으로 치환
    var resourcePrefix = name.ToLower().Replace(".", "-");
    File.WriteAllText(Path.Combine(root, "apphost.cs"), $"""
#:sdk Aspire.AppHost.Sdk@13.1.2

#pragma warning disable ASPIRECSHARPAPPS001

var builder = DistributedApplication.CreateBuilder(args);

// 1. TailwindCSS Watch 모드 (가장 먼저 실행)
// Blazor Auto 서버 프로젝트는 src/{name}.Web/{name}.Web/ 에 위치 (중첩 구조)
var webProjectDir = Path.Combine(builder.AppHostDirectory, "src", "{name}.Web", "{name}.Web");
var cssDir = Path.Combine(webProjectDir, "wwwroot", "css");
builder.AddExecutable("tailwindcss", "npx", webProjectDir,
    "@tailwindcss/cli",
    "-i", Path.Combine(cssDir, "tailwindcss_input.css"),
    "-o", Path.Combine(cssDir, "tailwindcss_output.css"),
    "--watch");

// 2. API 백엔드 (AddCSharpApp: ProjectReference 불필요)
var api = builder.AddCSharpApp("{resourcePrefix}-api", "src/{name}.Api/",
    options => options.LaunchProfileName = "https");

// 3. Blazor 프론트엔드 (AddCSharpApp: ProjectReference 불필요)
builder.AddCSharpApp("{resourcePrefix}-web", "src/{name}.Web/{name}.Web/",
    options => options.LaunchProfileName = "https")
    .WithReference(api)
    .WaitFor(api);

builder.Build().Run();
""", Encoding.UTF8);
    Print("  [OK] apphost.cs (file-based Aspire — AddCSharpApp + HTTPS)", ConsoleColor.Green);

    // ── API Program.cs 설정 (Swagger UI + Health Checks + CORS) ──────
    Print("");
    Print("  API Program.cs 구성 중...", ConsoleColor.White);
    var apiProgramCsPath = Path.Combine(root, "src", $"{name}.Api", "Program.cs");
    File.WriteAllText(apiProgramCsPath, $$"""
using Microsoft.OpenApi;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

// Swagger / OpenAPI (Development 환경에서만 UI 노출)
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "{{name}} API",
        Version = "v1",
        Description = "{{name}} Clean Architecture API"
    });
    // XML 주석 자동 포함 (GenerateDocumentationFile 활성화 시)
    var xmlFile = $"{System.Reflection.Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    if (File.Exists(xmlPath)) options.IncludeXmlComments(xmlPath);
});

// Health Checks
builder.Services.AddHealthChecks();

// CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowedOrigins", policy =>
        policy.WithOrigins(
                builder.Configuration["Cors:AllowedOrigins"]?.Split(',') ?? [])
              .AllowAnyMethod()
              .AllowAnyHeader()
              .AllowCredentials());
});

// Problem Details (RFC 7807)
builder.Services.AddProblemDetails();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c => c.SwaggerEndpoint("/swagger/v1/swagger.json", "{{name}} API v1"));
}

if (!app.Environment.IsDevelopment())
{
    app.UseHttpsRedirection();
    app.UseHsts();
}

app.UseCors("AllowedOrigins");
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();
app.MapHealthChecks("/health");
app.MapHealthChecks("/health/ready");

app.Run();
""", Encoding.UTF8);
    Print("  [OK] API/Program.cs (Swagger UI + Health Checks + CORS + Problem Details)", ConsoleColor.Green);

    // API 프로젝트에 XML 문서 생성 활성화 (Swagger XML 주석 지원)
    var apiCsprojPath = Path.Combine(root, "src", $"{name}.Api", $"{name}.Api.csproj");
    if (File.Exists(apiCsprojPath))
    {
        var csproj = File.ReadAllText(apiCsprojPath);
        if (!csproj.Contains("GenerateDocumentationFile"))
        {
            csproj = csproj.Replace("</PropertyGroup>",
                "    <GenerateDocumentationFile>true</GenerateDocumentationFile>\n" +
                "    <NoWarn>$(NoWarn);1591</NoWarn>\n" +
                "  </PropertyGroup>");
            File.WriteAllText(apiCsprojPath, csproj, Encoding.UTF8);
            Print("  [OK] API.csproj → XML 문서 생성 활성화 (1591 경고 억제)", ConsoleColor.Green);
        }
    }

    // .gitignore
    Run("dotnet", "new gitignore --output . --force", root);
    // Tailwind CSS 빌드 산출물 + Node.js 항목 추가
    var gitignorePath = Path.Combine(root, ".gitignore");
    if (File.Exists(gitignorePath))
    {
        File.AppendAllText(gitignorePath, """


# Tailwind CSS generated output (빌드 산출물 — Aspire watch 모드 출력)
**/wwwroot/css/tailwindcss_output.css

# Node.js (Tailwind CSS CLI)
**/node_modules/
**/package-lock.json
""", Encoding.UTF8);
    }
    Print("  [OK] .gitignore (tailwindcss_output.css + node_modules/ 추가)", ConsoleColor.Green);

    // global.json — SDK 버전 고정
    var dotnetVerFull = RunCapture("dotnet", "--version").Trim();
    var globalJson = "{\n  \"sdk\": {\n    \"version\": \"" + dotnetVerFull + "\",\n    \"rollForward\": \"latestMinor\"\n  }\n}";
    File.WriteAllText(Path.Combine(root, "global.json"), globalJson, Encoding.UTF8);
    Print($"  [OK] global.json (SDK {dotnetVerFull} 고정)", ConsoleColor.Green);

    // Directory.Build.props
    File.WriteAllText(Path.Combine(root, "Directory.Build.props"), $"""
<Project>
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
</Project>
""", Encoding.UTF8);
    Print("  [OK] Directory.Build.props", ConsoleColor.Green);

    // 패키지 버전은 dotnet add package 기본 동작(최신 stable)으로 각 .csproj에 자동 기록됨

    // README.md
    File.WriteAllText(Path.Combine(root, "README.md"), $"""
# {name}

> .NET 10 + Blazor Auto + Supabase Clean Architecture

## 기술 스택
- **언어**: C# / .NET 10
- **프론트엔드**: Blazor Auto (SSR + WASM)
- **백엔드**: ASP.NET Core Web API
- **오케스트레이션**: .NET Aspire (file-based apphost.cs)
- **DB**: Supabase (PostgreSQL)
- **스타일**: Tailwind CSS v4

## 프로젝트 구조

```
apphost.cs                 # Aspire 오케스트레이터 (file-based)
src/
  {name}.Domain/           # 엔터티, 도메인 이벤트, 값 객체
  {name}.Application/      # 유스케이스, 인터페이스, DTO
  {name}.Infrastructure/   # DB, 외부 서비스 구현체
  {name}.Api/              # ASP.NET Core Web API
  {name}.Web/              # Blazor Auto 프론트엔드
tests/
  {name}.Domain.Tests/
  {name}.Application.Tests/
```

## 빠른 시작

```bash
aspire run          # Aspire 실행 (TailwindCSS watch 포함)
dotnet build
dotnet test
```
""", Encoding.UTF8);
    Print("  [OK] README.md", ConsoleColor.Green);


    // ── Claude Forge 기능 복사 (.claude/) ─────────────────────
    Print("");
    Print("  Claude Forge 기능 복사 중...", ConsoleColor.White);
    var projectClaudeDir = Path.Combine(root, ".claude");
    Directory.CreateDirectory(projectClaudeDir);

    var forgeDirs = new[] { "agents", "rules", "commands", "skills", "hooks" };
    foreach (var d in forgeDirs)
    {
        var src = Path.Combine(repoDir, d);
        var dst = Path.Combine(projectClaudeDir, d);
        if (!Directory.Exists(src)) continue;
        if (Directory.Exists(dst)) Directory.Delete(dst, recursive: true);
        CopyDirectory(src, dst);
        Print($"  [OK] .claude/{d}/", ConsoleColor.DarkGray);
    }
    foreach (var f in new[] { "settings.json", "hooks.json" })
    {
        var src = Path.Combine(repoDir, f);
        var dst = Path.Combine(projectClaudeDir, f);
        if (File.Exists(src)) { File.Copy(src, dst, overwrite: true); Print($"  [OK] .claude/{f}", ConsoleColor.DarkGray); }
    }
    // 프로젝트용 CLAUDE.md
    File.WriteAllText(Path.Combine(root, "CLAUDE.md"), $"""
# {name}

.NET 10 + Blazor Auto + Supabase Clean Architecture 프로젝트

## 기술 스택
- **언어**: C# / .NET 10
- **프론트엔드**: Blazor Auto
- **백엔드**: .NET API (Clean Architecture)
- **DB**: Supabase (PostgreSQL)
- **스타일**: Tailwind CSS v4

## 빌드 & 검증 명령어

```bash
aspire run              # Aspire 실행 (TailwindCSS watch 포함)
dotnet build            # 빌드
dotnet test             # 테스트
dotnet format --verify-no-changes
```

## 핵심 디렉토리

```
apphost.cs                 # Aspire 오케스트레이터 (file-based)
src/{name}.Domain/         # 엔터티, 도메인
src/{name}.Application/    # 유스케이스
src/{name}.Infrastructure/ # DB, 외부 서비스
src/{name}.Api/            # Web API
src/{name}.Web/            # Blazor Auto
tests/                     # 단위·통합 테스트
.claude/                   # Claude Forge 기능 (agents, rules, commands, skills)
```
""", Encoding.UTF8);
    Print("  [OK] CLAUDE.md", ConsoleColor.Green);
    Print("  [OK] Claude Forge 기능 복사 완료", ConsoleColor.Green);

    // git init + 첫 커밋
    Print("");
    Print("  git 초기화 중...", ConsoleColor.White);
    Run("git", "init", root);
    Run("git", "add .", root);
    Run("git", $"commit -m \"chore: initial .NET Clean Architecture scaffold for {name}\"", root);
    Print("  [OK] git init + 첫 커밋 완료", ConsoleColor.Green);

    Print("");
    Print("  ╔══════════════════════════════════════════════════╗", ConsoleColor.Green);
    Print($"  ║   {name} 프로젝트 생성 완료!", ConsoleColor.Green);
    Print("  ╠══════════════════════════════════════════════════╣", ConsoleColor.Green);
    Print("  ║  5 src · 2 tests · apphost.cs · Claude Forge 포함 ║", ConsoleColor.Green);
    Print("  ╚══════════════════════════════════════════════════╝", ConsoleColor.Green);
    Print("");
    Print("  다음 단계:", ConsoleColor.Cyan);
    Print($"    cd \"{root}\"");
    Print("    aspire run             # Aspire 실행");
    Print("    dotnet build           # 빌드 확인");
    Print("    claude                 # Claude Code + Forge 사용 가능");
    Print("");
    Print("  ★ TailwindCSS v4 설정 완료 — aspire run 시 watch 모드 자동 시작", ConsoleColor.Yellow);
    Print("    Tailwind CLI 문서: https://tailwindcss.com/docs/installation/tailwind-cli", ConsoleColor.DarkGray);
    Print("  ★ Swagger UI: Aspire 대시보드에서 api 서비스 URL 확인 후 /swagger 접속", ConsoleColor.Yellow);
    Print("");
    Print($"  프로젝트 위치: {root}", ConsoleColor.Yellow);
}

// ══════════════════════════════════════════════
// 유틸리티 함수
// ══════════════════════════════════════════════

static void Print(string msg, ConsoleColor? color = null)
{
    if (color.HasValue) Console.ForegroundColor = color.Value;
    Console.WriteLine(msg);
    Console.ResetColor();
}

static bool CommandExists(string cmd)
{
    try
    {
        var psi = new ProcessStartInfo(cmd, "--version") { RedirectStandardOutput = true, RedirectStandardError = true, UseShellExecute = false };
        using var p = Process.Start(psi)!;
        p.WaitForExit();
        return true;
    }
    catch { return false; }
}

static int Run(string cmd, string args, string? workDir = null)
{
    try
    {
        var psi = new ProcessStartInfo(cmd, args) { UseShellExecute = false };
        if (workDir != null) psi.WorkingDirectory = workDir;
        using var p = Process.Start(psi)!;
        p.WaitForExit();
        return p.ExitCode;
    }
    catch { return -1; }
}

static string RunCapture(string cmd, string args, string? workDir = null)
{
    try
    {
        var psi = new ProcessStartInfo(cmd, args) { RedirectStandardOutput = true, RedirectStandardError = true, UseShellExecute = false };
        if (workDir != null) psi.WorkingDirectory = workDir;
        using var p = Process.Start(psi)!;
        var output = p.StandardOutput.ReadToEnd();
        p.WaitForExit();
        return output;
    }
    catch { return ""; }
}

static void DeletePath(string path)
{
    if (Directory.Exists(path)) Directory.Delete(path, recursive: true);
    else if (File.Exists(path)) File.Delete(path);
}

static void CopyDirectory(string src, string dest)
{
    Directory.CreateDirectory(dest);
    foreach (var file in Directory.GetFiles(src))
        File.Copy(file, Path.Combine(dest, Path.GetFileName(file)), overwrite: true);
    foreach (var dir in Directory.GetDirectories(src))
        CopyDirectory(dir, Path.Combine(dest, Path.GetFileName(dir)));
}
