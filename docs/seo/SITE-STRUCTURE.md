# Estrutura do Site (Arquitetura de URL)

A arquitetura do site foi desenhada para priorizar a facilidade de navegação dos usuários e a distribuição do "link juice" (PageRank interno) para as páginas principais.

## Hierarquia Atual e Futura

```text
/ (Homepage - Landing Page de Conversão. Foco: "Coach LoL")
│
├── /blog (Hub de Conteúdo Educacional)
│   ├── /blog/macro-gaming (Artigo)
│   ├── /blog/controle-de-wave (Artigo)
│   └── /blog/coach-humano-vs-ia (Artigo Comparativo)
│
├── /campeoes (Hub Programático - SEO Escalável)
│   ├── /campeoes/ahri (Dicas geradas pela IA)
│   ├── /campeoes/yasuo (Dicas geradas pela IA)
│   └── ... (160+ páginas baseadas em dados do LoL)
│
├── /sobre (Autoridade e Confiança - E-E-A-T)
│
├── /termos
└── /privacidade
```

## Estratégia de Linkagem Interna (Internal Linking)
- Todo artigo do `/blog` deve apontar com palavra-chave âncora exata (ex: "baixe nosso coach de lol") para a homepage `/`.
- As páginas do hub `/campeoes` devem ter links umas para as outras (ex: páginas de *counters* ou sinergias).
