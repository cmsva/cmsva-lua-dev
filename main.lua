local CoreGui, Workspace, Lighting = game:GetService("CoreGui"), game:GetService("Workspace"), game:GetService("Lighting")
local FixLagGUI = Instance.new("ScreenGui", CoreGui)
local MainFrame = Instance.new("Frame", FixLagGUI)
MainFrame.Size, MainFrame.Position, MainFrame.Active, MainFrame.Draggable, MainFrame.Visible = UDim2.new(0, 200, 0, 100), UDim2.new(0.5, -100, 0.5, -50), true, true, true

local function CreateBtn(name, text, pos)
    local btn = Instance.new("TextButton", MainFrame)
    btn.Size, btn.Position, btn.Text, btn.BackgroundColor3 = UDim2.new(0.9, 0, 0, 40), pos, text, Color3.fromRGB(50, 200, 50)
    return btn
end

local FixBtn, FPSBtn = CreateBtn("Fix", "Fix Lag: ON", UDim2.new(0.05, 0, 0.1, 0)), CreateBtn("FPS", "Max FPS: ON", UDim2.new(0.05, 0, 0.55, 0))
local gray = Instance.new("ColorCorrectionEffect", Lighting) gray.Saturation = -1

local function ToggleFix(state)
    FixBtn.BackgroundColor3 = state and Color3.fromRGB(50, 200, 50) or Color3.fromRGB(200, 50, 50)
    gray.Enabled = state
    Workspace.Terrain.WaterWaveSize = state and 0 or 0.15
    for _, v in pairs(Workspace:GetDescendants()) do
        if v:IsA("BasePart") and v.Name ~= "Baseplate" and v.Name ~= "Terrain" then v.Transparency = state and 1 or 0 end
        if v:IsA("ParticleEmitter") or v:IsA("Trail") or v:IsA("Beam") or v:IsA("Fire") then v.Enabled = not state end
    end
end

local function ToggleFPS(state)
    FPSBtn.BackgroundColor3 = state and Color3.fromRGB(50, 200, 50) or Color3.fromRGB(200, 50, 50)
    Lighting.GlobalShadows = not state
    settings().Rendering.QualityLevel = state and Enum.QualityLevel.Level01 or Enum.QualityLevel.Automatic
    for _, v in pairs(Lighting:GetDescendants()) do if v:IsA("PostEffect") and v ~= gray then v.Enabled = not state end end
end

FixBtn.MouseButton1Click:Connect(function() ToggleFix(not gray.Enabled) end)
FPSBtn.MouseButton1Click:Connect(function() ToggleFPS(Lighting.GlobalShadows) end)

-- Tự động bật
ToggleFix(true)
ToggleFPS(true)
