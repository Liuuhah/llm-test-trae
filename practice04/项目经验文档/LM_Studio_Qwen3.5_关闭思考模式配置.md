# Qwen3.5-9B 无思考模式配置
model: qwen/qwen3.5-9b-no-think
base: qwen/qwen3.5-9b  # 替换为你的实际模型路径

metadataOverrides:
  reasoning: false

customFields:
  - key: enableThinking
    displayName: "Enable Thinking"
    description: "Whether to allow thinking output before the final answer"
    type: boolean
    defaultValue: false
    effects:
      - type: setJinjaVariable
        variable: enable_thinking
