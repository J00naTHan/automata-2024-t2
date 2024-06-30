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
        raise Exception(f'filename expected type <str>, received type <{type(filename)}>')

    try:
        with open(filename, "rt") as file:
            lines, delta = file.readlines(), {}
            automata['sigma'] = lines[0].strip().split(' ')
            automata['is_nfa'] = epsilon_symbol in automata['sigma']
            automata['Q'] = set(lines[1].strip().split(' '))
            for q in lines[2].strip().split(' '):
                if q not in automata['Q']:
                    raise Exception(f'final state {q} not in Q')
            automata['F'] = set(lines[2].strip().split(' '))
            if lines[3].strip() in automata['Q']:
                automata['q0'] = lines[3].strip()
            else:
                raise Exception('initial state not in Q')
            for rule in lines[4:]:
                rule = rule.strip().split(' ')
                if len(rule) == 3:
                    if rule[0] in automata['Q'] and rule[2] in automata['Q'] and rule[1] in automata['sigma']:
                        if rule[0] not in delta:
                            delta[rule[0]] = {}
                        try:
                            rule = delta[rule[0]][rule[1]]
                            rule.append(rule[2])
                            if automata['is_nfa'] is False:
                                automata['is_nfa'] = True
                        except KeyError:
                            delta[rule[0]][rule[1]] = [rule[2]]
                    else:
                        raise Exception('transition rule states or symbol not valid')
                else:
                    raise Exception('transition rule has more or less than 3 parameters')
            automata['delta'] = delta
        if automata['is_nfa'] is True:
          automata = convert_to_dfa(automata)
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
      raise Exception(f'automata expected type <dict>, received type <{type(automata)}>, words expected type <list>, received type <{type(words)}>')

  try:
      Q = automata['Q']
      sigma = automata['sigma']
      q0 = automata['q0']
      F = automata['F']
      delta = automata['delta']
  except KeyError:
      raise Exception('automata is not a 5-uple')

  response = []
  for word in words:
      container, actual_q = None, q0
      for char in word:
          if container:
              break
          if char not in sigma:
              container = response.append((word, 'INVALIDA'))
              break
          for rule in delta:
              if rule[0] == actual_q and rule[1] == char:
                  actual_q = rule[2]
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


def convert_to_dfa(automata, epsilon_symbol='&'):
    """Converte um NFA num DFA."""

    if isinstance(automata, dict):
        try:
            Q = automata['Q']
            sigma = automata['sigma']
            q0 = automata['q0']
            F = automata['F']
            delta = automata['delta']
        except KeyError:
            raise Exception('automata is not a 5-uple')
    else:
        raise Exception(f'automata expected type: <dict>, received type: <{type(automata)}>')

    q0, e_closures = epsilon_closures(Q, q0, delta)

    # falta adicionar as regras do novo automato

    n_sigma = []
    for symbol in sigma:
        if symbol != epsilon_symbol:
            n_sigma.append(symbol)

    nQ_set = [set(q0.split('_'))]
    nQ = [q0]
    for q in nQ:
        for symbol in n_sigma:
            q = q.split('_')
            nq, q_rules, q_closure = '', [], set()
            for sub_q in q:
                try:
                    for rule in delta[sub_q][symbol]:
                        q_rules.append(rule)
                except KeyError:
                    None
                q_closure = q_closure.union(e_closures[sub_q])
            nq_set = q_closure.union(set(q_rules))
            if nq_set in nQ_set:
                continue
            nQ_set.union(nq_set)
            nq_set = list(nq_set)
            for q in nq_set:
                if q == nq_set[-1]:
                    nq += q
                else:
                    nq += f'{q}_'
            nQ.append(nq)
    nF = []
    for q in nQ:
        for qf in F:
            if qf in q:
                nF.append(q)
    nF = set(nF)


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
