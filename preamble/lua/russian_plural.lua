russian_plural = russian_plural or {}

function russian_plural.form(number, one, few, many)
  local n = math.abs(tonumber(number) or 0)
  local last_two = n % 100
  local last = n % 10

  if last_two >= 11 and last_two <= 14 then
    return many
  end

  if last == 1 then
    return one
  end

  if last >= 2 and last <= 4 then
    return few
  end

  return many
end
