if (Get-Command -Name ollama -ErrorAction SilentlyContinue) {
    ollama --version
    Write-Output '---OLLAMA LIST START---'
    $list = ollama list
    Write-Output $list
    Write-Output '---OLLAMA LIST END---'
    if ($list -match 'llama2') {
        Write-Output 'llama2 found — attempting generate...'
        ollama generate -m llama2 --no-stream --prompt 'You are Ravi: generate one concise merchantly line in-character.'
    } else {
        Write-Output 'MODEL_CHECK: llama2 not found in list'
    }
} else {
    Write-Output 'OLLAMA_NOT_FOUND'
}
