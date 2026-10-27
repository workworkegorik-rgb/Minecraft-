; Автокликер для AutoHotkey v2 (Windows): кликает при удержании ЛКМ или ПКМ
; Передняя боковая кнопка мыши: включение/выключение
#Requires AutoHotkey v2.0
#SingleInstance Force

CPS := 60 ; кликов в секунду
enabled := false

; Более точный Sleep (по умолчанию Windows округляет паузы до ~15.6 мс)
DllCall("winmm\timeBeginPeriod", "UInt", 1)

; Передняя боковая кнопка (XButton2, «Вперёд»)
; Знак * — срабатывает и с зажатыми Shift/Ctrl (например, когда крадёшься)
*XButton2::
{
    global enabled
    enabled := !enabled

    ToolTip enabled ? "Автокликер ON" : "Автокликер OFF"
    SetTimer () => ToolTip(), -1000
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

TrayTip "Нажми переднюю боковую кнопку мыши, чтобы включить", "Автокликер загружен"
