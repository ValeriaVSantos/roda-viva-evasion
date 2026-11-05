# Como subir esta pasta

1. Descompacte o arquivo recebido. Dentro dele há uma pasta chamada **experiments**.
2. Abra a página inicial de https://github.com/ValeriaVSantos/roda-viva-evasion e entre na sua conta.
3. Na raiz do repositório, clique em **Add file → Upload files**.
4. Arraste a pasta **experiments** inteira para a área de upload. Não envie o ZIP como um único arquivo e não arraste somente o conteúdo interno de `dach_css_2027`.
5. Confira a lista: os caminhos devem começar por `experiments/dach_css_2027/`.
6. Escreva a mensagem **Add DACH-CSS 2027 Qwen experiment and reproducible analysis** e finalize em **Commit changes**. Se preferir revisar em uma nova branch, use a opção de nova branch e abra o pull request oferecido pelo GitHub.
7. Abra `experiments/dach_css_2027/README.md` no GitHub e confirme que ele aparece formatado e que os arquivos estão acessíveis.

Essa pasta acrescenta uma nova experiência ao repositório. Os arquivos existentes da raiz, `scripts/`, `data/`, `results/` e `paper/` não precisam ser substituídos.

Depois do upload, uma indicação opcional no README principal é:

```markdown
## DACH-CSS 2027 experiment

The historical Qwen prompt comparison, exact prompt variants, labels-only snapshot,
and reproducible evaluation are available in
[experiments/dach_css_2027](experiments/dach_css_2027/README.md).
```

O Colab original continha credenciais escritas no código. A cópia incluída neste pacote remove as credenciais, as saídas e metadados desnecessários. Se as chaves originais ainda estiverem ativas, revogue-as na Groq e use novas chaves em **Secrets** no Colab. Não suba o notebook original sem essa limpeza.

Para reproduzir os números, comece pelo notebook `02_reproduce_metrics.ipynb` ou pela instrução de uma linha no README. O notebook `01_original_colab_sanitized.ipynb` serve como registro histórico: contém células sobrepostas de execução e retomada, e não deve ser executado inteiro como roteiro de uma nova experiência.

Instruções oficiais de upload: https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository
