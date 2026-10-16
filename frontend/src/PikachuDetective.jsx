
import './PikachuDetective.css'

function PikachuDetective({ pose = 'idle' }) {
  return (
    <div
      className={`pikachu-stage pikachu-${pose}`}
      role="img"
      aria-label={
        pose === 'investigating'
          ? 'Pikachu is investigating with a magnifying glass'
          : pose === 'success'
            ? 'Pikachu celebrates solving the case'
            : 'Pikachu waits curiously for evidence'
      }
    >
      <div className="pikachu-aura" />

      <svg
        className="pikachu-character"
        viewBox="0 0 280 330"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <defs>
          <linearGradient id="pikachuFur" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#ffe982" />
            <stop offset="100%" stopColor="#f5bd35" />
          </linearGradient>

          <linearGradient id="magnifierGlass" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#ffffff" stopOpacity=".7" />
            <stop offset="100%" stopColor="#9fe8f7" stopOpacity=".18" />
          </linearGradient>
        </defs>

        {/* Ears */}
        <g className="pikachu-ears">
          <path
            d="M91 104 Q57 83 48 29 Q45 12 61 24 L111 76Z"
            fill="url(#pikachuFur)"
            stroke="#b98126"
            strokeWidth="2"
          />
          <path
            d="M53 32 Q70 48 98 84 L86 85 Q65 64 53 32"
            fill="#40302b"
          />
          <path
            d="M174 78 Q211 34 224 24 Q236 16 231 38 L205 105Z"
            fill="url(#pikachuFur)"
            stroke="#b98126"
            strokeWidth="2"
          />
          <path
            d="M224 27 L230 36 Q213 61 197 80 L195 67Z"
            fill="#40302b"
          />
        </g>

        {/* Body */}
        <path
          d="M99 211 Q81 235 91 279 Q109 301 140 297 Q174 302 190 278 Q199 242 177 211Z"
          fill="url(#pikachuFur)"
          stroke="#b98126"
          strokeWidth="2"
        />

        {/* Feet */}
        <ellipse cx="111" cy="291" rx="28" ry="12" fill="#f7ca54" />
        <ellipse cx="169" cy="291" rx="28" ry="12" fill="#f7ca54" />

        {/* Tail */}
        <path
          className="pikachu-tail"
          d="M184 246 L211 228 L205 206 L231 211 L225 237 L245 250 L222 270 L198 265Z"
          fill="#f5c542"
          stroke="#b98126"
          strokeWidth="2"
        />

        {/* Arms */}
        <g className="pikachu-arms">
          <path
            d="M94 222 Q68 235 84 257 Q95 266 109 249"
            fill="#ffdf70"
            stroke="#b98126"
            strokeWidth="2"
          />
          <path
            d="M179 221 Q204 230 194 252 Q184 263 169 248"
            fill="#ffdf70"
            stroke="#b98126"
            strokeWidth="2"
          />
        </g>

        {/* Head */}
        <path
          d="M73 126 Q70 89 103 82 Q139 66 175 83 Q213 95 207 133 L200 181 Q183 213 140 215 Q96 212 79 181Z"
          fill="url(#pikachuFur)"
          stroke="#b98126"
          strokeWidth="2"
        />

        {/* Detective cap */}
        <g className="pikachu-cap">
          <path
            d="M74 104 Q78 66 126 65 Q174 61 201 98 L205 109 Q144 94 74 111Z"
            fill="#9b6a3d"
            stroke="#68452e"
            strokeWidth="2"
          />
          <path
            d="M62 108 Q127 88 211 106 Q221 113 204 119 Q130 106 70 123Z"
            fill="#775032"
            stroke="#68452e"
            strokeWidth="2"
          />
          <path
            d="M126 65 Q138 53 151 67 L146 85 L130 83Z"
            fill="#b88654"
            stroke="#68452e"
            strokeWidth="2"
          />
          <path d="M88 91 Q131 77 172 91" fill="none" stroke="#d2a16b" strokeWidth="3" strokeLinecap="round" />
        </g>

        {/* Eyebrows */}
        <path className="pikachu-brows" d="M96 133 Q108 123 120 132 M158 132 Q171 123 183 134"
          fill="none" stroke="#72502d" strokeWidth="3" strokeLinecap="round" />

        {/* Eyes */}
        <g className="pikachu-eyes">
          <ellipse cx="109" cy="150" rx="11" ry="16" fill="#392b27" />
          <ellipse cx="169" cy="150" rx="11" ry="16" fill="#392b27" />
          <ellipse cx="112" cy="145" rx="4" ry="6" fill="#fff" />
          <ellipse cx="172" cy="145" rx="4" ry="6" fill="#fff" />
          <path d="M98 138 L93 132 M104 135 L102 128 M165 135 L164 128 M176 137 L181 131"
            stroke="#392b27" strokeWidth="2" strokeLinecap="round" />
        </g>

        {/* Eyelids blink over the eyes */}
        <g className="pikachu-blink">
          <path d="M94 144 Q109 128 124 144 Q110 155 94 144Z" fill="#edbd43" />
          <path d="M154 144 Q169 128 184 144 Q170 155 154 144Z" fill="#edbd43" />
        </g>

        {/* Cheeks */}
        <ellipse className="pikachu-cheek pikachu-cheek-left" cx="86" cy="173" rx="15" ry="11" fill="#f47778" />
        <ellipse className="pikachu-cheek pikachu-cheek-right" cx="192" cy="173" rx="15" ry="11" fill="#f47778" />

        {/* Nose and smile */}
        <path d="M135 164 Q140 160 145 164 Q140 171 135 164Z" fill="#51352b" />
        <path d="M140 171 Q132 183 123 176 M140 171 Q148 183 157 176"
          fill="none" stroke="#51352b" strokeWidth="2.5" strokeLinecap="round" />

        {/* Investigation magnifying glass */}
        <g className="pikachu-magnifier">
          <circle cx="191" cy="143" r="27" fill="#9fe8f7" fillOpacity=".25" stroke="#8b633c" strokeWidth="7" />
          <circle cx="191" cy="143" r="22" fill="url(#magnifierGlass)" stroke="#f7d986" strokeWidth="2" />
          <path d="M211 164 L235 190" stroke="#68452e" strokeWidth="11" strokeLinecap="round" />
          <path d="M210 164 L234 188" stroke="#d1a06b" strokeWidth="5" strokeLinecap="round" />
          <path d="M180 132 Q188 124 196 130" fill="none" stroke="#fff" strokeWidth="3" strokeLinecap="round" />
        </g>

        {/* Victory sunglasses */}
        <g className="pikachu-sunglasses">
          <path d="M91 137 Q109 128 127 138 L124 157 Q108 165 98 155Z" fill="#171817" stroke="#080908" strokeWidth="3" />
          <path d="M151 138 Q169 128 187 137 L180 155 Q169 165 154 157Z" fill="#171817" stroke="#080908" strokeWidth="3" />
          <path d="M126 141 Q139 136 152 141" fill="none" stroke="#171817" strokeWidth="5" />
          <path className="pikachu-glass-shine" d="M100 140 L114 136 L108 145Z" fill="#fff" />
          <path d="M160 140 L174 136 L168 145Z" fill="#fff" />
        </g>

        {/* Folded arms in victory pose */}
        <g className="pikachu-folded-arms">
          <path d="M94 237 Q124 259 160 238 Q177 229 187 244 Q177 269 142 270 Q108 270 88 250Z"
            fill="#ffdc70" stroke="#b98126" strokeWidth="3" />
          <path d="M105 252 Q137 263 171 245" fill="none" stroke="#b98126" strokeWidth="3" strokeLinecap="round" />
        </g>
      </svg>

      {/* Animated investigation spark */}
      <div className="pikachu-search-spark" aria-hidden="true">✦</div>

      {/* Animated shine over the success sunglasses */}
      <div className="pikachu-victory-spark" aria-hidden="true">✦</div>

      <p className="pikachu-caption">
        {pose === 'investigating'
          ? 'SEARCHING FOR CLUES…'
          : pose === 'success'
            ? 'CASE SOLVED!'
            : 'READY, DETECTIVE?'}
      </p>
    </div>
  )
}

export default PikachuDetective
