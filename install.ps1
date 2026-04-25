#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$ProjectPath,

    [ValidateSet("claude", "cc", "ccnest")]
    [string]$LaunchCommand = "claude",

    [string]$SettingsPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-WindowsTerminalSettingsPath {
    $candidates = @(
        (Join-Path $env:LOCALAPPDATA "Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"),
        (Join-Path $env:LOCALAPPDATA "Microsoft\Windows Terminal\settings.json")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    throw "Windows Terminal settings.json was not found. Install Windows Terminal or pass -SettingsPath."
}

function Convert-ToArray {
    param([object]$Value)

    if ($null -eq $Value) {
        return @()
    }

    if ($Value -is [System.Array]) {
        return @($Value)
    }

    return @($Value)
}

function Get-JsonPropertyValue {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Object,

        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $null
    }

    return $property.Value
}

function New-ClaudeShortcutAction {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Id,

        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$Action,

        [string]$Split,

        [Parameter(Mandatory = $true)]
        [string]$CommandLine,

        [Parameter(Mandatory = $true)]
        [string]$StartingDirectory
    )

    $command = [ordered]@{
        action            = $Action
        commandline       = $CommandLine
        startingDirectory = $StartingDirectory
    }

    if ($Split) {
        $command.split = $Split
    }

    [pscustomobject][ordered]@{
        command = [pscustomobject]$command
        id      = $Id
        name    = $Name
    }
}

function New-ClaudeKeybinding {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Id,

        [Parameter(Mandatory = $true)]
        [string]$Keys
    )

    [pscustomobject][ordered]@{
        id   = $Id
        keys = $Keys
    }
}

$resolvedProjectPath = (Resolve-Path -LiteralPath $ProjectPath).Path

if (-not $SettingsPath) {
    $SettingsPath = Get-WindowsTerminalSettingsPath
}

if (-not (Test-Path -LiteralPath $SettingsPath)) {
    throw "Settings file does not exist: $SettingsPath"
}

$backupPath = "$SettingsPath.bak-$(Get-Date -Format yyyyMMdd-HHmmss)"
Copy-Item -LiteralPath $SettingsPath -Destination $backupPath

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$rawSettings = [System.IO.File]::ReadAllText($SettingsPath, $utf8NoBom)
$settings = $rawSettings | ConvertFrom-Json

if ($null -eq $settings.PSObject.Properties["actions"]) {
    $settings | Add-Member -MemberType NoteProperty -Name actions -Value @()
}

if ($null -eq $settings.PSObject.Properties["keybindings"]) {
    $settings | Add-Member -MemberType NoteProperty -Name keybindings -Value @()
}

$commandLine = "cmd /k $LaunchCommand"
$reserveCtrlTForNestedTabs = $LaunchCommand -eq "ccnest"
$managedActionIds = @(
    "ClaudeTerminalShortcuts.SplitRight",
    "ClaudeTerminalShortcuts.SplitDown",
    "ClaudeTerminalShortcuts.NewTab"
)
$managedKeys = @("ctrl+d", "ctrl+e", "ctrl+t")

$newActions = @(
    (New-ClaudeShortcutAction `
        -Id "ClaudeTerminalShortcuts.SplitRight" `
        -Name "Claude: split right" `
        -Action "splitPane" `
        -Split "right" `
        -CommandLine $commandLine `
        -StartingDirectory $resolvedProjectPath),
    (New-ClaudeShortcutAction `
        -Id "ClaudeTerminalShortcuts.SplitDown" `
        -Name "Claude: split down" `
        -Action "splitPane" `
        -Split "down" `
        -CommandLine $commandLine `
        -StartingDirectory $resolvedProjectPath)
)

if (-not $reserveCtrlTForNestedTabs) {
    $newActions += (New-ClaudeShortcutAction `
        -Id "ClaudeTerminalShortcuts.NewTab" `
        -Name "Claude: new tab" `
        -Action "newTab" `
        -CommandLine $commandLine `
        -StartingDirectory $resolvedProjectPath)
}

$newKeybindings = @(
    (New-ClaudeKeybinding -Id "ClaudeTerminalShortcuts.SplitRight" -Keys "ctrl+d"),
    (New-ClaudeKeybinding -Id "ClaudeTerminalShortcuts.SplitDown" -Keys "ctrl+e")
)

if (-not $reserveCtrlTForNestedTabs) {
    $newKeybindings += (New-ClaudeKeybinding -Id "ClaudeTerminalShortcuts.NewTab" -Keys "ctrl+t")
}

$existingActions = Convert-ToArray $settings.actions
$settings.actions = @(
    $existingActions | Where-Object {
        $existingId = Get-JsonPropertyValue -Object $_ -Name "id"
        $managedActionIds -notcontains $existingId
    }
) + $newActions

$existingKeybindings = Convert-ToArray $settings.keybindings
$settings.keybindings = @(
    $existingKeybindings | Where-Object {
        $existingId = Get-JsonPropertyValue -Object $_ -Name "id"
        $existingKeys = Convert-ToArray (Get-JsonPropertyValue -Object $_ -Name "keys")
        $hasManagedId = $managedActionIds -contains $existingId
        $hasManagedKey = $false

        foreach ($key in $existingKeys) {
            if ($managedKeys -contains ([string]$key).ToLowerInvariant()) {
                $hasManagedKey = $true
            }
        }

        -not ($hasManagedId -or $hasManagedKey)
    }
) + $newKeybindings

$updatedJson = $settings | ConvertTo-Json -Depth 64
[System.IO.File]::WriteAllText($SettingsPath, $updatedJson + [Environment]::NewLine, $utf8NoBom)

Write-Host "Claude Terminal Shortcuts installed."
Write-Host "Project path: $resolvedProjectPath"
Write-Host "Launch command: $LaunchCommand"
if ($reserveCtrlTForNestedTabs) {
    Write-Host "Ctrl+T: reserved for ccnest internal tabs"
}
Write-Host "Settings file: $SettingsPath"
Write-Host "Backup file: $backupPath"

# Version History
# ver0.1 - 2026-04-25 - Added non-destructive Windows Terminal shortcut installer with backup and UTF-8 output.
# ver0.2 - 2026-04-25 - Reserved Ctrl+T for ccnest internal tabs while keeping terminal tabs for claude and cc.
