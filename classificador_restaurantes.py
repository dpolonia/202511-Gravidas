#!/usr/bin/env python3
"""
Classificador de Respostas de Clientes de Restaurantes
-----------------------------------------------------
Classifica reviews de restaurantes em categorias e sentimentos.
"""

import re
from typing import Dict, List, Tuple
from collections import defaultdict


class ClassificadorRestaurante:
    """Classifica respostas de clientes de restaurantes."""

    def __init__(self):
        # Palavras-chave para análise de sentimento
        self.palavras_positivas = {
            'excelente', 'ótimo', 'maravilhoso', 'perfeito', 'delicioso',
            'saboroso', 'bom', 'agradável', 'fantástico', 'incrível',
            'recomendo', 'adorei', 'amei', 'gostei', 'qualidade',
            'fresco', 'limpo', 'rápido', 'atencioso', 'simpático'
        }

        self.palavras_negativas = {
            'ruim', 'péssimo', 'horrível', 'terrível', 'fraco',
            'frio', 'cru', 'queimado', 'demorado', 'sujo',
            'caro', 'mal', 'nojento', 'decepcionante', 'insatisfeito',
            'mal-educado', 'grosseiro', 'lento', 'fila', 'espera'
        }

        # Palavras-chave para categorias
        self.categorias = {
            'comida': {
                'comida', 'prato', 'refeição', 'sabor', 'tempero',
                'carne', 'peixe', 'massa', 'salada', 'sobremesa',
                'porção', 'qualidade', 'ingrediente', 'fresco'
            },
            'serviço': {
                'atendimento', 'garçom', 'garçonete', 'serviço',
                'staff', 'equipe', 'funcionário', 'atenção',
                'simpático', 'educado', 'rápido', 'demorou'
            },
            'ambiente': {
                'ambiente', 'lugar', 'espaço', 'decoração',
                'limpo', 'sujo', 'música', 'barulho', 'confortável',
                'aconchegante', 'vista', 'atmosfera'
            },
            'preço': {
                'preço', 'caro', 'barato', 'custo', 'valor',
                'pagamento', 'conta', 'em conta', 'vale a pena',
                'cobrar', 'cobrança'
            }
        }

    def limpar_texto(self, texto: str) -> str:
        """Remove caracteres especiais e normaliza o texto."""
        texto = texto.lower()
        texto = re.sub(r'[^\w\s]', ' ', texto)
        return texto

    def analisar_sentimento(self, texto: str) -> Tuple[str, float]:
        """
        Analisa o sentimento do texto.

        Returns:
            Tuple com (sentimento, score)
            - sentimento: 'positivo', 'negativo' ou 'neutro'
            - score: pontuação entre -1 (muito negativo) e +1 (muito positivo)
        """
        texto_limpo = self.limpar_texto(texto)
        palavras = texto_limpo.split()

        score_positivo = sum(1 for palavra in palavras if palavra in self.palavras_positivas)
        score_negativo = sum(1 for palavra in palavras if palavra in self.palavras_negativas)

        total_palavras = len(palavras)
        if total_palavras == 0:
            return 'neutro', 0.0

        # Calcular score normalizado
        score = (score_positivo - score_negativo) / total_palavras

        # Classificar sentimento
        if score > 0.05:
            sentimento = 'positivo'
        elif score < -0.05:
            sentimento = 'negativo'
        else:
            sentimento = 'neutro'

        return sentimento, score

    def identificar_categorias(self, texto: str) -> Dict[str, int]:
        """
        Identifica as categorias mencionadas no texto.

        Returns:
            Dict com contagem de menções por categoria
        """
        texto_limpo = self.limpar_texto(texto)
        palavras = set(texto_limpo.split())

        mencoes = {}
        for categoria, palavras_chave in self.categorias.items():
            count = len(palavras.intersection(palavras_chave))
            if count > 0:
                mencoes[categoria] = count

        return mencoes

    def classificar(self, texto: str) -> Dict:
        """
        Classifica completamente uma resposta de cliente.

        Returns:
            Dict com análise completa
        """
        sentimento, score = self.analisar_sentimento(texto)
        categorias = self.identificar_categorias(texto)

        return {
            'texto': texto,
            'sentimento': sentimento,
            'score_sentimento': round(score, 3),
            'categorias_mencionadas': categorias,
            'categoria_principal': max(categorias.keys(), key=categorias.get) if categorias else 'geral'
        }

    def classificar_multiplos(self, reviews: List[str]) -> List[Dict]:
        """Classifica múltiplas reviews."""
        return [self.classificar(review) for review in reviews]

    def gerar_resumo(self, reviews: List[str]) -> Dict:
        """
        Gera um resumo estatístico de múltiplas reviews.

        Returns:
            Dict com estatísticas agregadas
        """
        classificacoes = self.classificar_multiplos(reviews)

        # Contar sentimentos
        sentimentos = defaultdict(int)
        for c in classificacoes:
            sentimentos[c['sentimento']] += 1

        # Contar categorias
        categorias_totais = defaultdict(int)
        for c in classificacoes:
            for cat, count in c['categorias_mencionadas'].items():
                categorias_totais[cat] += count

        # Calcular score médio
        score_medio = sum(c['score_sentimento'] for c in classificacoes) / len(classificacoes)

        return {
            'total_reviews': len(reviews),
            'distribuicao_sentimento': dict(sentimentos),
            'categorias_mais_mencionadas': dict(sorted(categorias_totais.items(),
                                                       key=lambda x: x[1],
                                                       reverse=True)),
            'score_medio': round(score_medio, 3),
            'reviews_classificadas': classificacoes
        }


def exibir_resultado(resultado: Dict):
    """Exibe o resultado de forma formatada."""
    print("\n" + "="*60)
    print("ANÁLISE DE REVIEW")
    print("="*60)
    print(f"\nTexto: {resultado['texto'][:100]}...")
    print(f"\n📊 Sentimento: {resultado['sentimento'].upper()}")
    print(f"   Score: {resultado['score_sentimento']}")

    if resultado['categorias_mencionadas']:
        print(f"\n🏷️  Categorias mencionadas:")
        for cat, count in resultado['categorias_mencionadas'].items():
            print(f"   - {cat.capitalize()}: {count} menções")
        print(f"\n⭐ Categoria principal: {resultado['categoria_principal'].upper()}")
    else:
        print("\n🏷️  Nenhuma categoria específica identificada")


def exibir_resumo(resumo: Dict):
    """Exibe o resumo de múltiplas reviews."""
    print("\n" + "="*60)
    print("RESUMO DAS REVIEWS")
    print("="*60)
    print(f"\n📈 Total de reviews analisadas: {resumo['total_reviews']}")
    print(f"\n📊 Distribuição de Sentimento:")
    for sent, count in resumo['distribuicao_sentimento'].items():
        percentual = (count / resumo['total_reviews']) * 100
        print(f"   {sent.capitalize()}: {count} ({percentual:.1f}%)")

    print(f"\n💯 Score médio: {resumo['score_medio']}")

    print(f"\n🏷️  Categorias mais mencionadas:")
    for cat, count in list(resumo['categorias_mais_mencionadas'].items())[:5]:
        print(f"   {cat.capitalize()}: {count} menções")


# ============================================================================
# EXEMPLOS DE USO
# ============================================================================

def main():
    """Exemplos de uso do classificador."""

    print("🍽️  CLASSIFICADOR DE REVIEWS DE RESTAURANTES")
    print("="*60)

    # Criar instância do classificador
    classificador = ClassificadorRestaurante()

    # Exemplo 1: Review individual positiva
    print("\n📝 EXEMPLO 1: Review Positiva")
    review1 = "A comida estava deliciosa! O atendimento foi excelente e o ambiente muito agradável. Recomendo!"
    resultado1 = classificador.classificar(review1)
    exibir_resultado(resultado1)

    # Exemplo 2: Review individual negativa
    print("\n📝 EXEMPLO 2: Review Negativa")
    review2 = "Péssimo serviço! A comida chegou fria e o garçom foi muito mal-educado. Muito caro para a qualidade."
    resultado2 = classificador.classificar(review2)
    exibir_resultado(resultado2)

    # Exemplo 3: Review neutra/mista
    print("\n📝 EXEMPLO 3: Review Mista")
    review3 = "A comida é boa mas o preço é um pouco elevado. O ambiente é ok."
    resultado3 = classificador.classificar(review3)
    exibir_resultado(resultado3)

    # Exemplo 4: Análise de múltiplas reviews
    print("\n📝 EXEMPLO 4: Análise de Múltiplas Reviews")
    reviews_multiplas = [
        "Adorei! Comida maravilhosa e atendimento rápido.",
        "Ambiente aconchegante mas a comida estava fria.",
        "Péssimo! Demorou muito e estava horrível.",
        "Ótimo restaurante, recomendo muito!",
        "Bom custo-benefício, voltarei com certeza.",
        "O garçom foi atencioso mas a comida não estava fresca.",
        "Lugar limpo e organizado, gostei bastante!",
        "Muito caro para o que oferece."
    ]

    resumo = classificador.gerar_resumo(reviews_multiplas)
    exibir_resumo(resumo)

    print("\n" + "="*60)
    print("✅ Análise concluída!")
    print("="*60)


if __name__ == "__main__":
    main()
