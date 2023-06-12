export default defineNuxtPlugin(() => {
    return {
        provide: {
            copyTextToClipboard
        }
    }
})

function copyTextToClipboard(text: string) {
    const div = document.createElement("div")
    div.innerText = text
    document.body.appendChild(div)

    const r = document.createRange()
    r.selectNode(div)
    // @ts-ignore
    window.getSelection().removeAllRanges()
    // @ts-ignore
    window.getSelection().addRange(r)
    document.execCommand('copy')
    // @ts-ignore
    window.getSelection().removeAllRanges()

    document?.body?.removeChild(div)
}
