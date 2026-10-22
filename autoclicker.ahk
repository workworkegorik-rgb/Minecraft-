; Автокликер для AutoHotkey v2 (Windows): кликает при удержании ЛКМ или ПКМ
; Клавиша R: включение/выключение
#Requires AutoHotkey v2.0
#SingleInstance Force

CPS := 60 ; кликов в секунду
enabled := false

; Более точный Sleep (по умолчанию Windows округляет паузы до ~15.6 мс)
DllCall("winmm\timeBeginPeriod", "UInt", 1)

; Клавиша R: sc013 — физическая клавиша, работает и на русской раскладке
; Знак ~ пропускает нажатие дальше, чтобы клавиша работала как обычно
~sc013::
~+sc013::
{
    global enabled
    enabled := !enabled

    ToolTip enabled ? "Автокликер ON" : "Автокликер OFF"
    SetTimer () => ToolTip(), -1000

    ; Игнорируем автоповтор при удержании клавиши
    KeyWait "sc013"
}

; Пока автокликер включён, удержание ЛКМ или ПКМ запускает клики
#HotIf enabled
~LButton::
~RButton::
{
    while enabled && (GetKeyState("LButton", "P") || GetKeyState("RButton", "P")) {
        if GetKeyState("LButton", "P")
            Click
        if GetKeyState("RButton", "P")
            Click "Right"
        Sleep 1000 // CPS
    }
}
#HotIf

TrayTip "Нажми R, чтобы включить", "Автокликер загружен"
