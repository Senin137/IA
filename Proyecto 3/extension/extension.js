const vscode = require("vscode");

const API_URL = "http://127.0.0.1:5000/autocompletar";

async function autocompletarConRNN() {
    const editor = vscode.window.activeTextEditor;

    if (!editor) {
        vscode.window.showErrorMessage("No hay un editor abierto.");
        return;
    }

    const documento = editor.document;
    const posicionCursor = editor.selection.active;

    const rango = new vscode.Range(
        new vscode.Position(0, 0),
        posicionCursor
    );

    const codigo = documento.getText(rango);

    if (!codigo || codigo.trim() === "") {
        vscode.window.showWarningMessage("Escribe código antes de autocompletar.");
        return;
    }

    const config = vscode.workspace.getConfiguration("kzRnnAutocomplete");
    const apiUrl = config.get("apiUrl", API_URL);
    const maxTokens = config.get("maxTokens", 500);

    await vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: "Generando autocompletado con RNN...",
            cancellable: false,
        },
        async () => {
            try {
                const respuesta = await fetch(apiUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        codigo: codigo,
                        max_tokens: maxTokens,
                    }),
                });

                if (!respuesta.ok) {
                    const texto = await respuesta.text();
                    vscode.window.showErrorMessage(
                        `Error en la API (${respuesta.status}): ${texto}`
                    );
                    return;
                }

                const datos = await respuesta.json();
                const completado = datos.completado || "";

                if (completado.trim() === "") {
                    vscode.window.showInformationMessage(
                        "La RNN no generó autocompletado."
                    );
                    return;
                }

                await editor.edit((editBuilder) => {
                    editBuilder.insert(posicionCursor, completado);
                });

                vscode.window.showInformationMessage(
                    `Autocompletado insertado (${completado.length} caracteres).`
                );
            } catch (error) {
                vscode.window.showErrorMessage(
                    "No se pudo conectar con la API local. Verifica que esté corriendo: python servidor_api.py"
                );
            }
        }
    );
}

function activate(context) {
    const comando = vscode.commands.registerCommand(
        "kzRnnAutocomplete.autocompletar",
        autocompletarConRNN
    );

    context.subscriptions.push(comando);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate,
};