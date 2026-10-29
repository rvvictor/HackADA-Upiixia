type LogoProps = {
  /** Text size class, e.g. "text-xl" or "text-[6rem]". */
  className?: string;
  /** Light "colon" for dark backgrounds. */
  oscuro?: boolean;
  /** Show the hexagon mark before the word. */
  marca?: boolean;
};

/** colonIA: the "IA" always in rosa mexicano. */
export function Logo({ className = "text-xl", oscuro = false, marca = true }: LogoProps) {
  return (
    <span className={`pb-display inline-flex items-center gap-[0.3em] font-extrabold ${className}`} aria-label="colonIA">
      {marca && <MarcaHex />}
      <span aria-hidden="true">
        <span className={oscuro ? "text-(--pb-hero-texto)" : "text-(--pb-texto)"}>colon</span>
        <span className="text-(--pb-marca)">IA</span>
      </span>
    </span>
  );
}

/** Three H3-like hexagons: the neighborhood network. */
export function MarcaHex({ className = "h-[1.05em] w-[1.05em]" }: { className?: string }) {
  const hex = "M12 2.5 20.2 7.25v9.5L12 21.5l-8.2-4.75v-9.5z";
  return (
    <svg viewBox="0 0 48 44" className={className} aria-hidden="true">
      <path d={hex} transform="translate(0 0) scale(1)" fill="var(--pb-marca)" />
      <path d={hex} transform="translate(17 0) scale(1)" fill="var(--pb-cempasuchil)" />
      <path d={hex} transform="translate(8.5 14.5) scale(1)" fill="var(--pb-jade)" />
    </svg>
  );
}
