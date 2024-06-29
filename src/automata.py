"""Implementação de autômatos finitos."""


# lembrar de ver se "epsilon_symbol" não dá erro nos testes
def load_automata(filename, epsilon_symbol='&'):
    """
    Lê os dados de um autômato finito a partir de um arquivo.

    A estsrutura do arquivo deve ser:

    <lista de símbolos do alfabeto, separados por espaço (' ')>
    <lista de nomes de estados>
    <lista de nomes de estados finais>
    <nome do estado inicial>
    <lista de regras de transição, com "origem símbolo destino">

    Um exemplo de arquivo válido é:

    ```
    a b
    q0 q1 q2 q3
    q0 q3
    q0
    q0 a q1
    q0 b q2
    q1 a q0
    q1 b q3
    q2 a q3
    q2 b q0
    q3 a q1
    q3 b q2
    ```

    Caso o arquivo seja inválido uma exceção Exception é gerada.
    """

    if isinstance(filename, str):
        automata = {}
        if not filename.endswith('.txt'):
            filename += '.txt'
    else:
        raise Exception('The filename type should be: str')

    try:
        with open(filename, "rt") as file:
            lines, delta = file.readlines(), {}
            automata['sigma'] = lines[0].strip().split(' ')
            automata['is_nfa'] = True if epsilon_symbol in automata['sigma'] else False
            automata['Q'] = set(lines[1].strip().split(' '))
            F = lines[2].strip().split(' ')
            for q in F:
                if q not in automata['Q']:
                    raise Exception('Final states has to be existing states')
            automata['F'] = set(F)
            if lines[3].strip() in automata['Q']:
                automata['q0'] = lines[3].strip()
            else:
                raise Exception('initial state has to be an existing state')
            for line in lines[4:]:
                line = line.strip().split(' ')
                if len(line) == 3:
                    if line[0] in automata['Q'] and line[2] in automata['Q'] and line[1] in automata['sigma']:
                        if automata['is_nfa'] is False and delta[line[0]][line[1]]:
                            automata['is_nfa'] = True
                        delta[line[0]][line[1]] = line[2]
                    else:
                        raise Exception('the states or the symbol for this transition is not valid')
                else:
                    raise Exception('transition rules have 3 (three) parameters')
            automata['delta'] = delta
        return automata
    except FileNotFoundError:
        raise Exception('file not found')


def process(automata, words):
    """
    Processa a lista de palavras e retora o resultado.
    
    Os resultados válidos são ACEITA, REJEITA, INVALIDA.
    """

    if isinstance(automata, dict) and isinstance(words, list):
        for w in words:
            if not isinstance(w, str):
                raise Exception('word type should be <str>')
    else:
        raise Exception('automata type should be <dict> and words type should be <str>')

    try:
        is_nfa = automata['is_nfa']
    except KeyError:
        raise Exception('the determinism of this automata is not determinable')

    if is_nfa is True:
        automata = convert_to_dfa(automata)
    try:
        Q = automata['Q']
        sigma = automata['sigma']
        q0 = automata['q0']
        F = automata['F']
        delta = automata['delta']
    except KeyError:
        raise Exception('the automata does not match the 5-uple format')

    # não muda mais
    response = []
    for word in words:
        container = None
        actual_q = q0
        for char in word:
            if container:
                break
            if char not in sigma:
                container = response.append((word, 'INVALIDA'))
                break
            for rule in delta:
                if rule[0] == aq and rule[1] == char:
                    aq = rule[2]
                    break
            else:
                container = response.append((word, 'REJEITA'))
                break
        else:
            if actual_q in F:
                container = response.append((word, 'ACEITA'))
            else:
                container = response.append((word, 'REJEITA'))
    return dict(response)


def convert_to_dfa(automata):
    """Converte um NFA num DFA."""

    if isinstance(automata, dict):
        try:
            Q = automata['Q']
            sigma = automata['sigma']
            q0 = automata['q0']
            F = automata['F']
            delta = automata['delta']
        except KeyError:
            raise Exception('automata not complete')
    else:
        raise Exception(f'automata expected type: <dict>\nautomata received type: <{type(automata)}>')

    q0, e_closures = epsilon_closures(Q, q0, delta)

    nQ = [q0]
    for q in nQ:
        for symbol in automata['sigma']:
            try:
                for rule in automata['rules'][q][symbol]:
                    if rule not in nQ:
                        nQ.append(rule)
            except KeyError:
                pass


def epsilon_closures(Q, q0, delta, epsilon_symbol='&'):
    """Encontra feixes epsilon para um automato"""

    e_q0, e_closures = '', {}
    for q in Q:
        e_closure = [q]
        epsilon_rules = None
        for q in e_closure:
            try:
                epsilon_rules = delta[q][epsilon_symbol]
                for qf in epsilon_rules:
                    if qf not in e_closure:
                        e_closure.append(qf)
            except KeyError:
                epsilon_rules = None
        if epsilon_rules is None:
            if q == q0:
                for q in e_closure:
                    if q == e_closure[-1]:
                        e_q0 += f'{q}'
                    else:
                        e_q0 += f'{q}_'
            e_closure = set(e_closure)
            e_closures[q] = e_closure
    return e_q0, e_closures
