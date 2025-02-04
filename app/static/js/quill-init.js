
var quillController = new QuillNotesManager()
var quill = new Quill("#note-quill",
    {
        "theme":"snow",
        "placeholder":"Your notes goes here..."
    }
)


quill.on("text-change", (delta, oldDelta, source) => {
    quillController.intervalStart()
});
