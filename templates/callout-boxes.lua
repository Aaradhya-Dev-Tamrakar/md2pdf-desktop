-- Converts fenced divs like ::: {.callout} ... ::: into LaTeX tcolorbox
-- environments defined in templates/styled.latex.
-- Supported classes: .callout -> calloutbox, .answer -> answerbox

local ENV_MAP = {
  callout = "calloutbox",
  answer  = "answerbox",
}

function Div(el)
  for class, env in pairs(ENV_MAP) do
    if el.classes:includes(class) then
      local blocks = {}
      table.insert(blocks, pandoc.RawBlock("latex", "\\begin{" .. env .. "}"))
      for _, b in ipairs(el.content) do
        table.insert(blocks, b)
      end
      table.insert(blocks, pandoc.RawBlock("latex", "\\end{" .. env .. "}"))
      return blocks
    end
  end
  return el
end
