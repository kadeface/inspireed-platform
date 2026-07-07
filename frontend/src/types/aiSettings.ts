export interface AIChannelSettings {
  base_url: string
  model: string
  max_tokens: number
  temperature: number
}

export interface AISettingsResponse {
  text: AIChannelSettings
  self_study_vision: AIChannelSettings
  api_key_configured: boolean
  api_key_source: string
}

export interface AISettingsUpdateRequest {
  text: AIChannelSettings
  self_study_vision: AIChannelSettings
}
