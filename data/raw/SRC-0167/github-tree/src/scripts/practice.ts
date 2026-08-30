const QUESTION_PATTERN = /^(?:문제\s*\d+|Q\d+)\b/i;
const MULTIPLE_PATTERN = /(?:select|choose)\s+(?:two|three|2|3)|(?:두|세)\s*개|복수\s*선택/i;
const TRUE_FALSE_PATTERN = /true\s*(?:\/|or)?\s*false|참\s*(?:\/|또는)?\s*거짓/i;

type Question = {
  readonly card: HTMLElement;
  readonly heading: HTMLHeadingElement;
  readonly options: readonly HTMLLIElement[];
  readonly details?: HTMLDetailsElement;
};

function directQuestionList(card: HTMLElement): HTMLUListElement | undefined {
  for (const child of card.children) {
    if (child instanceof HTMLUListElement && child.nextElementSibling instanceof HTMLDetailsElement) {
      return child;
    }
  }
}

function addBinaryOptions(card: HTMLElement): HTMLUListElement | undefined {
  const details = card.querySelector(':scope > details');
  if (!(details instanceof HTMLDetailsElement)) return;

  const list = document.createElement('ul');
  const labels = TRUE_FALSE_PATTERN.test(card.textContent ?? '')
    ? ['True / 참', 'False / 거짓']
    : ['Yes / 예', 'No / 아니요'];
  for (const label of labels) {
    const item = document.createElement('li');
    item.textContent = label;
    list.append(item);
  }
  details.before(list);
  return list;
}

function makeOptionsInteractive(list: HTMLUListElement, isMultiple: boolean): readonly HTMLLIElement[] {
  const options = Array.from(list.children).filter(
    (item): item is HTMLLIElement => item instanceof HTMLLIElement,
  );
  list.classList.add('practice-options');
  list.setAttribute('role', isMultiple ? 'group' : 'radiogroup');

  const select = (selected: HTMLLIElement) => {
    if (!isMultiple) {
      for (const option of options) {
        option.classList.remove('is-selected');
        option.setAttribute('aria-checked', 'false');
      }
    }
    const nextState = !selected.classList.contains('is-selected');
    selected.classList.toggle('is-selected', nextState);
    selected.setAttribute('aria-checked', String(nextState));
    document.dispatchEvent(new CustomEvent('practice:change'));
  };

  for (const option of options) {
    option.tabIndex = 0;
    option.setAttribute('role', isMultiple ? 'checkbox' : 'radio');
    option.setAttribute('aria-checked', 'false');
    option.addEventListener('click', () => select(option));
    option.addEventListener('keydown', (event) => {
      if (event.key !== 'Enter' && event.key !== ' ') return;
      event.preventDefault();
      select(option);
    });
  }
  return options;
}

function groupQuestions(content: HTMLElement): readonly Question[] {
  const wrappers = Array.from(content.querySelectorAll(':scope > .sl-heading-wrapper.level-h3')).filter(
    (wrapper): wrapper is HTMLElement => {
      if (!(wrapper instanceof HTMLElement)) return false;
      const heading = wrapper.querySelector('h3');
      return heading instanceof HTMLHeadingElement && QUESTION_PATTERN.test(heading.textContent?.trim() ?? '');
    },
  );

  return wrappers.map((wrapper, index) => {
    const headingElement = wrapper.querySelector('h3');
    if (!(headingElement instanceof HTMLHeadingElement)) {
      throw new TypeError('Practice heading wrapper must contain an h3 element.');
    }
    const heading = headingElement;
    const card = document.createElement('section');
    card.className = 'practice-question';
    card.id = `practice-question-${index + 1}`;
    card.setAttribute('aria-labelledby', heading.id || `${card.id}-title`);
    if (!heading.id) heading.id = `${card.id}-title`;
    wrapper.before(card);

    let node: ChildNode | null = wrapper;
    while (node) {
      if (
        node !== wrapper &&
        node instanceof HTMLElement &&
        node.classList.contains('sl-heading-wrapper') &&
        (node.classList.contains('level-h2') || node.classList.contains('level-h3'))
      ) {
        break;
      }
      const nextNode: ChildNode | null = node.nextSibling;
      card.append(node);
      node = nextNode;
    }

    const questionText = card.textContent ?? '';
    const list = directQuestionList(card) ?? addBinaryOptions(card);
    const options = list ? makeOptionsInteractive(list, MULTIPLE_PATTERN.test(questionText)) : [];
    const detailsElement = card.querySelector(':scope > details');
    const details = detailsElement instanceof HTMLDetailsElement ? detailsElement : undefined;
    details?.addEventListener('toggle', () => {
      card.classList.toggle('is-reviewed', details.open);
      document.dispatchEvent(new CustomEvent('practice:change'));
    });

    const actions = document.createElement('div');
    actions.className = 'practice-actions';
    const reset = document.createElement('button');
    reset.type = 'button';
    reset.textContent = '선택 초기화 / Reset';
    reset.addEventListener('click', () => {
      for (const option of options) {
        option.classList.remove('is-selected');
        option.setAttribute('aria-checked', 'false');
      }
      document.dispatchEvent(new CustomEvent('practice:change'));
    });
    const next = document.createElement('button');
    next.type = 'button';
    next.textContent = '다음 문제 / Next';
    next.addEventListener('click', () => {
      const nextCard = card.nextElementSibling;
      if (nextCard instanceof HTMLElement && nextCard.classList.contains('practice-question')) {
        nextCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
        nextCard.querySelector<HTMLElement>('[role="radio"], [role="checkbox"], summary')?.focus();
      }
    });
    actions.append(reset, next);
    card.append(actions);
    return { card, heading, options, details };
  });
}

function addDashboard(questions: readonly Question[]): void {
  const dashboard = document.createElement('aside');
  dashboard.className = 'practice-dashboard';
  dashboard.setAttribute('aria-label', '문제 풀이 진행률');

  const label = document.createElement('p');
  label.className = 'practice-dashboard__label';
  label.setAttribute('aria-live', 'polite');
  const progress = document.createElement('progress');
  progress.max = questions.length;
  const jump = document.createElement('button');
  jump.type = 'button';
  jump.textContent = '다음 미풀이 / Next unanswered';
  jump.addEventListener('click', () => {
    const target = questions.find(({ options }) => !options.some((option) => option.classList.contains('is-selected')));
    target?.card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    target?.card.querySelector<HTMLElement>('[role="radio"], [role="checkbox"], summary')?.focus();
  });
  dashboard.append(label, progress, jump);
  questions[0]?.card.before(dashboard);

  const update = () => {
    const answered = questions.filter(({ options }) =>
      options.some((option) => option.classList.contains('is-selected')),
    ).length;
    const reviewed = questions.filter(({ details }) => details?.open).length;
    progress.value = answered;
    label.textContent = `선택 ${answered}/${questions.length} · 해설 확인 ${reviewed}/${questions.length}`;
  };
  document.addEventListener('practice:change', update);
  update();
}

export function initializePractice(): void {
  const content = document.querySelector('.sl-markdown-content');
  if (!(content instanceof HTMLElement) || content.dataset.practiceEnhanced === 'true') return;

  const questions = groupQuestions(content);
  if (questions.length === 0) return;
  content.dataset.practiceEnhanced = 'true';
  content.classList.add('practice-content');
  addDashboard(questions);
}
