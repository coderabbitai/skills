# Validate the packaged catalog before publishing it to "coderabbit skills".
require "rubygems/package"
require "yaml"
require "zlib"

archive, version = ARGV
abort "Usage: ruby #{$PROGRAM_NAME} ARCHIVE VERSION" unless ARGV.length == 2

prefix = "coderabbit-skills-#{version}/skills/"
expected = Dir.children("skills").select { |name| File.directory?(File.join("skills", name)) }
abort "No skill directories found in tagged checkout" if expected.empty?
catalog = {}

Zlib::GzipReader.open(archive) do |gzip|
  Gem::Package::TarReader.new(gzip).each do |entry|
    next unless entry.full_name.start_with?(prefix)
    next if entry.directory?

    name, path = entry.full_name.delete_prefix(prefix).split("/", 2)
    next unless path
    abort "Unexpected skill directory: #{name}" unless expected.include?(name)
    abort "Non-regular skill file: #{entry.full_name}" unless entry.file?
    next unless path == "SKILL.md"
    abort "Duplicate entry: #{entry.full_name}" if catalog.key?(name)

    source = entry.read.force_encoding("UTF-8")
    header = source[/\A---\r?\n(.*?)\r?\n---(?:\r?\n|\z)/m, 1]
    abort "#{name}/SKILL.md: missing frontmatter" unless header
    data = YAML.safe_load(header)
    abort "#{name}/SKILL.md: expected a YAML mapping" unless data.is_a?(Hash)

    # The installer reads these two scalar fields from individual lines.
    # Check the YAML meaning as well, so an unrelated nested version cannot pass.
    declared_name = header[/^name:[ \t]*["']?([a-z0-9]+(?:-[a-z0-9]+)*)["']?[ \t]*\r?$/, 1]
    unless data["name"] == name && declared_name == name
      abort "#{name}/SKILL.md: name must match its directory"
    end
    skill_version = data["metadata"].is_a?(Hash) && data["metadata"]["version"]
    declared_version = header[/^[ \t]+version:[ \t]*["']?([^"'\r\n]+?)["']?[ \t]*\r?$/, 1]
    unless skill_version.is_a?(String) && !skill_version.strip.empty? && declared_version == skill_version
      abort "#{name}/SKILL.md: missing or unreadable metadata.version"
    end
    catalog[name] = skill_version
  end
end

missing = expected - catalog.keys
abort "Missing from archive: #{missing.sort.join(', ')}" unless missing.empty?
puts catalog.sort.map { |name, skill_version| "#{name} #{skill_version}" }
