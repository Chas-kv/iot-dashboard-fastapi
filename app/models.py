from pydantic import BaseModel, Field

class ModeChange(BaseModel):
    mode: int = Field(..., ge=0, le=1, description="0: Manual, 1: Automático")

class ServoMove(BaseModel):
    angle: int = Field(..., ge=0, le=180, description="Ángulo del servo (0 a 180)")

class SystemStatus(BaseModel):
    temperature: float | None
    humidity: float | None
    lumen: int | None
    servo_value: int | None
    door_state: bool | None
    mode: int
