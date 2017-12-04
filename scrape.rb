require 'nokogiri'
require 'httparty'
require 'sqlite3'

page = HTTParty.get "https://www.koket.se/mat/ingredienser/korv"
urls = page.scan(/(?<=<h2><a href="\/)([^"]*)/)

open("output.txt", "a") do |f|
urls.each do |url|
	recipe_page = HTTParty.get "https://www.koket.se/" + url[0]
	
	page_parse = Nokogiri::HTML(recipe_page)
	
	
	ingrs = page_parse.css('#ingredients').css('.ingredient').text
	
	items = ingrs.split("\n").map! {|x| x.strip}
	
	(0...items.length).each do |i|
		if i % 3 == 0
			items[i] = nil
		end
	end
	
	items.compact!
	
	ingredients = []
	
	(0...items.length/2).each do |i|
		ingredients[i] = [items[i*2], items[i*2+1]]
	end

	#db = SQLite3::Database.open "recipes.sqlite3"

	ingredients.each do |ingredient|
		#db.execute "INSERT INTO recipes VALUES ( \"#{ingredient[0]}\", \"#{ingredient[1]}\" );"
		f.puts "#{ingredient[0]} #{ingredient[1]}\n"
	end
end
end
