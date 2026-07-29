export function LinePeople() {
  return (
    <svg className="line-people" viewBox="0 0 680 250" role="img" aria-label="两条线从两边靠近，在中间留下一段空间">
      <path className="line-people__coral" d="M0 205h118c21 0 32-11 32-31v-67c0-31 13-52 39-52 23 0 36 21 36 52v71c0 18 10 27 28 27h62" />
      <circle className="line-people__coral" cx="188" cy="28" r="18" />
      <path className="line-people__navy" d="M680 205H562c-21 0-32-11-32-31v-67c0-31-13-52-39-52-23 0-36 21-36 52v71c0 18-10 27-28 27h-62" />
      <circle className="line-people__navy" cx="492" cy="28" r="18" />
      <path className="line-people__gap" d="M315 205h50" />
    </svg>
  );
}
