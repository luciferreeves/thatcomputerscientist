Clear-Host

$CYAN   = "Cyan"
$GREEN  = "Green"
$YELLOW = "Yellow"
$BLUE   = "Blue"
$PURPLE = "Magenta"
$RED    = "Red"

$LANG_CODE = "ja"

function Write-Color {
    param (
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

Write-Color " ████████╗██████╗  █████╗ ███╗   ██╗███████╗██╗      █████╗ ████████╗███████╗" $CYAN
Write-Color " ╚══██╔══╝██╔══██╗██╔══██╗████╗  ██║██╔════╝██║     ██╔══██╗╚══██╔══╝██╔════╝" $CYAN
Write-Color "    ██║   ██████╔╝███████║██╔██╗ ██║███████╗██║     ███████║   ██║   █████╗  " $CYAN
Write-Color "    ██║   ██╔══██╗██╔══██║██║╚██╗██║╚════██║██║     ██╔══██║   ██║   ██╔══╝  " $CYAN
Write-Color "    ██║   ██║  ██║██║  ██║██║ ╚████║███████║███████╗██║  ██║   ██║   ███████╗" $CYAN
Write-Color "    ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝" $CYAN

Write-Color ""
Write-Color "   ᕕ(⌐■_■)ᕗ Locale generation tool for Japanese templates" $PURPLE
Write-Color ""

function Generate-Messages {
    Write-Color ""
    Write-Color "Generating translation messages for $LANG_CODE (HTML templates and Python files)..." $YELLOW
    Write-Color ""

    python manage.py makemessages -l $LANG_CODE -e html,py --ignore templates.old/* --ignore venv/* --ignore env/* --ignore .venv/*

    if ($LASTEXITCODE -ne 0) {
        Write-Color "Error: makemessages failed" $RED
        exit 1
    }

    Write-Color ""
    Write-Color "✓ Translation message files successfully generated!" $GREEN
    Write-Color "You can now edit the .po files in locale/$LANG_CODE/LC_MESSAGES/" $BLUE
    Write-Color ""
}

function Compile-Messages {
    $localePath = "locale/$LANG_CODE/LC_MESSAGES"

    Write-Color ""
    Write-Color "Compiling translation messages for $LANG_CODE..." $YELLOW
    Write-Color ""

    if (-not (Test-Path $localePath)) {
        Write-Color "Error: $localePath directory not found." $RED
        exit 1
    }

    Push-Location $localePath

    if (-not (Test-Path django.po)) {
        Write-Color "Error: django.po not found." $RED
        Write-Color "Tip: Run the generate option first to create translation files." $YELLOW
        Pop-Location
        exit 1
    }

    Write-Color "Compiling django.po..." $BLUE
    msgfmt django.po -o django.mo

    if ($LASTEXITCODE -ne 0) {
        Write-Color "Error: Failed to compile django.po" $RED
        Pop-Location
        exit 1
    }

    Write-Color "✓ Compiled django.mo successfully." $GREEN
    Pop-Location
    Write-Color ""
    Write-Color "✓ Translation messages compilation complete!" $GREEN
    Write-Color ""
}

if ($args.Count -gt 0) {
    if ($args[0] -eq "-g") {
        Generate-Messages
    }
    elseif ($args[0] -eq "-c") {
        Compile-Messages
    }
    else {
        Write-Color "Invalid option. Use -g or -c." $RED
        exit 1
    }
}
else {
    Write-Color "What do you want to do?" $CYAN
    Write-Color "  g - Generate translation messages" $GREEN
    Write-Color "  c - Compile translation messages" $BLUE
    Write-Host -NoNewline "Choose an option " -ForegroundColor $YELLOW
    Write-Host -NoNewline "[" -ForegroundColor White
    Write-Host -NoNewline "g" -ForegroundColor $GREEN
    Write-Host -NoNewline "]: " -ForegroundColor White

    $action = Read-Host
    if ([string]::IsNullOrWhiteSpace($action)) {
        $action = "g"
    }

    if ($action -eq "g") {
        Generate-Messages
    }
    elseif ($action -eq "c") {
        Compile-Messages
    }
    else {
        Write-Color "Error: Invalid option. Use 'g' for generate or 'c' for compile." $RED
        exit 1
    }
}


