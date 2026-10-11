-- Автокликер для Hammerspoon: кликает при удержании ЛКМ или ПКМ
-- Клавиша R: включение/выключение
local types = hs.eventtap.event.types
local props = hs.eventtap.event.properties
local MARKER = 987654321
local CLICK_INTERVAL = 1 / 80 -- интервал между кликами, как в исходном скрипте
local KEY_R = 15 -- код физической клавиши R (работает и на русской раскладке)
local enabled = false

-- Состояние для каждой кнопки мыши
local buttons = {
    left = {
        downType = types.leftMouseDown,
        upType = types.leftMouseUp,
        held = false,
        timer = nil,
    },
    right = {
        downType = types.rightMouseDown,
        upType = types.rightMouseUp,
        held = false,
        timer = nil,
    },
}

-- Отправляем искусственный клик нужной кнопкой
local function sendClick(btn)
    if not enabled or not btn.held then return end

    local pos = hs.mouse.absolutePosition()

    local down = hs.eventtap.event.newMouseEvent(btn.downType, pos)
    local up = hs.eventtap.event.newMouseEvent(btn.upType, pos)

    down:setProperty(props.eventSourceUserData, MARKER)
    up:setProperty(props.eventSourceUserData, MARKER)

    down:post()
    up:post()
end

local function startClicking(btn)
    if btn.held then return end

    btn.held = true
    btn.timer = hs.timer.doEvery(CLICK_INTERVAL, function()
        sendClick(btn)
    end)
end

local function stopClicking(btn)
    btn.held = false

    if btn.timer then
        btn.timer:stop()
        btn.timer = nil
    end
end

local function stopAll()
    for _, btn in pairs(buttons) do
        stopClicking(btn)
    end
end

-- Отслеживаем физические ЛКМ и ПКМ
mouseWatcher = hs.eventtap.new({
    types.leftMouseDown,
    types.leftMouseUp,
    types.rightMouseDown,
    types.rightMouseUp,
}, function(event)
    -- Игнорируем собственные клики макроса
    if event:getProperty(props.eventSourceUserData) == MARKER then
        return false
    end

    if not enabled then return false end

    local eventType = event:getType()
    for _, btn in pairs(buttons) do
        if eventType == btn.downType then
            startClicking(btn)
        elseif eventType == btn.upType then
            stopClicking(btn)
        end
    end

    return false
end)
mouseWatcher:start()

-- Клавиша R: включение/выключение
keyWatcher = hs.eventtap.new({ types.keyDown }, function(event)
    if event:getKeyCode() ~= KEY_R then return false end

    -- Игнорируем автоповтор при удержании клавиши
    if event:getProperty(props.keyboardEventAutorepeat) ~= 0 then
        return false
    end

    -- Не реагируем на сочетания вроде Cmd+R
    local flags = event:getFlags()
    if flags.cmd or flags.ctrl or flags.alt then return false end

    enabled = not enabled
    stopAll()

    hs.alert.show(
        enabled and "Автокликер ON" or "Автокликер OFF"
    )

    -- Пропускаем нажатие R дальше, чтобы клавиша работала как обычно
    return false
end)
keyWatcher:start()

hs.alert.show("Макрос загружен")
