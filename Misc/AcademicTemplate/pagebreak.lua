-- pagebreak.lua: converts \newpage (plain text paragraph) to an HTML/CSS page break.
-- Works in the pandoc HTML+WeasyPrint pipeline.

local BREAK = pandoc.RawBlock("html", '<div style="break-before: page;"></div>')

function Para(el)
  if #el.content == 1 then
    local item = el.content[1]
    if item.t == "Str" and item.text == "\\newpage" then
      return BREAK
    end
    -- also handle raw latex inlines (if raw_tex is ever enabled)
    if item.t == "RawInline" and item.format == "tex" and item.text:match("^\\newpage") then
      return BREAK
    end
  end
end

function RawBlock(el)
  if el.format == "tex" and el.text:match("^\\newpage") then
    return BREAK
  end
end
