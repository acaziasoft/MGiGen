# -*- coding: utf-8 -*-
# Created by Tuan Truong on 2018-08-28.
# © 2018 Framgia.
# v1.0.0

import sys
import os
from datetime import datetime
import subprocess
import re
from jinja2 import Environment, PackageLoader

#=================== Helpers ===================

def pasteboard_read():
	return subprocess.check_output('pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8')

def camel_case(st):
	return st[0].lower() + st[1:]

#=================== Constants ===================

FILE_HEADER = "file_header.txt"

#=================== BaseTemplate ===================

class Template(object):

	class Model(object):
		def __init__(self, name, properties):
			super(Template.Model, self).__init__()
			self.name = name
			self.properties = properties


	class Property(object):
		def __init__(self, property):
			super(Template.Property, self).__init__()
			self.property = property
			property_regex = re.compile("(?:let|var) (\w+): (.*)")
			mo = property_regex.search(property)
			self.name = mo.group(1)
			self.name_title = self.name.title()
			self.type = Template.PropertyType(mo.group(2))

		@property
		def is_url(self):
			lowered_name = self.name.lower()
			if lowered_name.endswith("id"):
				return False
			return "image" in lowered_name or "url" in lowered_name
		

	class PropertyType(object):
		def __init__(self, name):
			super(Template.PropertyType, self).__init__()
			self.name = name

		def is_optional(self):
			return self.name.endswith("?")

		def is_array(self):
			return self.name.endswith(("]", "]?"))

	class TemplateType:
		BASE = "-base"
		LIST = "-list"
		DETAIL = "-detail"

	def parse_model(self, model_text):
		model_regex = re.compile("(?:struct|class) (\w+) {((.|\n)*)}")
		match = model_regex.search(model_text)
		model_name = match.group(1)
		property_block = match.group(2)
		property_regex = re.compile("(?:let|var) (\w+): (.*)")
		properties = [Template.Property(p.group()) for p in property_regex.finditer(property_block)]
		return Template.Model(model_name, properties)

	class BaseTemplate(object):
		def __init__(self, name, project, developer, company, date):
			super(Template.BaseTemplate, self).__init__()
			self.name = name
			self.project = project
			self.developer = developer
			self.company = company
			self.date = date
			self.env = Environment(
				loader=PackageLoader('templates', 'base'),
				trim_blocks=True,
				lstrip_blocks=True
			)

		def _create_file(self, class_name, content):
			file_name = class_name + ".swift"
			file_path = "{}/{}.swift".format(self.name, class_name)
			self.__create_file(file_path, file_name, content)

		def _create_test_file(self, class_name, content):
			file_name = class_name + ".swift"
			file_path = "{}/Test/{}.swift".format(self.name, class_name)
			self.__create_file(file_path, file_name, content)

		def __create_file(self, file_path, file_name, content):
			with open(file_path, "w") as f:
				f.write(content.encode('utf8'))
				print("        new file:   {}".format(file_path))

		def _file_header(self, class_name):
			template = self.env.get_template("header.swift")
			header = template.render(
				class_name=class_name,
				project=self.project,
				developer=self.developer,
				created_date=self.date,
				copyright_year=datetime.now().year,
				company=self.company
			)
			return header + "\n\n"

		def create_files(self):
			print(" ")
			self._make_dirs()
			self._create_view_model()
			self._create_navigator()
			self._create_use_case()
			self._create_view_controller()
			self._create_assembler()
			# Test
			self._create_view_model_tests()
			self._create_use_case_mock()
			self._create_navigator_mock()
			self._create_view_controller_tests()
			print(" ")

		def _make_dirs(self):
			current_directory = os.getcwd()
			main_directory = os.path.join(current_directory, r'{}'.format(self.name))
			try: 
				os.makedirs(main_directory)
			except:
				pass
			test_directory = os.path.join(main_directory, "Test")
			try:
				os.makedirs(test_directory)
			except:
				pass

		def _create_view_model(self):
			class_name = self.name + "ViewModel"
			template = self.env.get_template("ViewModel.swift")
			content = self._file_header(class_name)
			content += template.render(
				name=self.name
			)
			self._create_file(class_name, content)

		def _create_navigator(self):
			class_name = self.name + "Navigator"
			template = self.env.get_template("Navigator.swift")
			content = self._file_header(class_name)
			content += template.render(
				name=self.name
			)
			self._create_file(class_name, content)

		def _create_use_case(self):
			class_name = self.name + "UseCase"
			template = self.env.get_template("UseCase.swift")
			content = self._file_header(class_name)
			content += template.render(
				name=self.name
			)
			self._create_file(class_name, content)

		def _create_view_controller(self):
			class_name = self.name + "ViewController"
			template = self.env.get_template("ViewController.swift")
			content = self._file_header(class_name)
			content += template.render(
				name=self.name
			)
			self._create_file(class_name, content)

		def _create_assembler(self):
			class_name = self.name + "Assembler"
			template = self.env.get_template("Assembler.swift")
			content = self._file_header(class_name)
			content += template.render(
				name=self.name
			)
			self._create_file(class_name, content)

		def _create_view_model_tests(self):
			class_name = self.name + "ViewModelTests"
			template = self.env.get_template("ViewModelTests.swift")
			content = self._file_header(class_name)
			content += template.render(
				name=self.name,
				project=self.project
			)
			self._create_test_file(class_name, content)

		def _create_use_case_mock(self):
			class_name = self.name + "UseCaseMock"
			template = self.env.get_template("UseCaseMock.swift")
			content = self._file_header(class_name)
			content += template.render(
				name=self.name,
				project=self.project
			)
			self._create_test_file(class_name, content)

		def _create_navigator_mock(self):
			class_name = self.name + "NavigatorMock"
			template = self.env.get_template("NavigatorMock.swift")
			content = self._file_header(class_name)
			content += template.render(
				name=self.name,
				project=self.project
			)
			self._create_test_file(class_name, content)

		def _create_view_controller_tests(self):
			class_name = self.name + "ViewControllerTests"
			template = self.env.get_template("ViewControllerTests.swift")
			content = self._file_header(class_name)
			content += template.render(
				name=self.name,
				project=self.project
			)
			self._create_test_file(class_name, content)



	#=================== ListTemplate ===================

	class ListTemplate(BaseTemplate):

		def __init__(self, model, options, name, project, developer, company, date):
			super(Template.ListTemplate, self).__init__(name, project, developer, company, date)
			self.model = model
			self.options = options
			self.is_sectioned_list = "--section" in options
			self.is_collection = "--collection" in options
			self.model_name = self.model.name
			self.model_variable = camel_case(self.model_name)
			self.env = Environment(
				loader=PackageLoader('templates', 'list'),
				trim_blocks=True,
				lstrip_blocks=True
			)

		def create_files(self):
			print(" ")
			self._make_dirs()
			self._create_view_model()
			self._create_item_view_model()
			self._create_navigator()
			self._create_use_case()
			self._create_view_controller()
			self._create_table_view_cell()
			self._create_assembler()
			# Test
			self._create_view_model_tests()
			self._create_use_case_mock()
			self._create_navigator_mock()
			self._create_view_controller_tests()
			self._create_table_view_cell_tests()
			print(" ")

		def _create_view_model(self):
			class_name = self.name + "ViewModel"
			if self.is_sectioned_list:
				template_name = "SectionedViewModel.swift"
			else:
				template_name = "ViewModel.swift"
			template = self.env.get_template(template_name)
			content = self._file_header(class_name)
			content += template.render(
				name=self.name,
				model_name=self.model_name,
				model_variable=self.model_variable
			)
			self._create_file(class_name, content)

		def _create_item_view_model(self):
			class_name = self.model_name + "ViewModel"
			template = self.env.get_template("ItemViewModel.swift")
			content = self._file_header(class_name)
			content += template.render(
				model_name=self.model_name,
				model_variable=self.model_variable,
				properties=self.model.properties
			)
			self._create_file(class_name, content)

		def _create_use_case(self):
			class_name = self.name + "UseCase"
			template = self.env.get_template("UseCase.swift")
			content = self._file_header(class_name)
			content += template.render(
				name=self.name,
				model_name=self.model_name
			)
			self._create_file(class_name, content)

		def _create_navigator(self):
			class_name = self.name + "Navigator"
			template = self.env.get_template("Navigator.swift")
			content = self._file_header(class_name)
			content += template.render(
				name=self.name,
				model_name=self.model_name,
				model_variable=self.model_variable
			)
			self._create_file(class_name, content)

		def _create_view_controller(self):
			class_name = self.name + "ViewController"
			if self.is_sectioned_list:
				if self.is_collection:
					template_file = "SectionedCollectionViewController.swift"
				else:
					template_file = "SectionedTableViewController.swift"
			else:
				if self.is_collection:
					template_file = "CollectionViewController.swift"
				else:
					template_file = "TableViewController.swift"
			template = self.env.get_template(template_file)
			content = self._file_header(class_name)
			content += template.render(
				name=self.name,
				model_name=self.model_name,
				model_variable=self.model_variable
			)
			self._create_file(class_name, content)

		def _create_table_view_cell(self):
			class_name = self.model_name + "Cell"
			if self.is_collection:
				template_file = "CollectionViewCell.swift"
			else:
				template_file = "TableViewCell.swift"
			template = self.env.get_template(template_file)
			content = self._file_header(class_name)
			content += template.render(
				model_name=self.model_name,
				model_variable=self.model_variable,
				properties=self.model.properties
			)
			self._create_file(class_name, content)

		def _create_view_model_tests(self):
			class_name = self.name + "ViewModelTests"
			if self.is_sectioned_list:
				template_name = "SectionedViewModelTests.swift"
			else:
				template_name = "ViewModelTests.swift"
			template = self.env.get_template(template_name)
			content = self._file_header(class_name)
			content += template.render(
				project=self.project,
				name=self.name,
				model_name=self.model_name,
				model_variable=self.model_variable
			)
			self._create_test_file(class_name, content)

		def _create_use_case_mock(self):
			class_name = self.name + "UseCaseMock"
			template = self.env.get_template("UseCaseMock.swift")
			content = self._file_header(class_name)
			content += template.render(
				project=self.project,
				name=self.name,
				model_name=self.model_name
			)
			self._create_test_file(class_name, content)

		def _create_navigator_mock(self):
			class_name = self.name + "NavigatorMock"
			template = self.env.get_template("NavigatorMock.swift")
			content = self._file_header(class_name)
			content += template.render(
				project=self.project,
				name=self.name,
				model_name=self.model_name,
				model_variable=self.model_variable
			)
			self._create_test_file(class_name, content)

		def _create_view_controller_tests(self):
			class_name = self.name + "ViewControllerTests"
			if self.is_collection:
				template_name = "CollectionViewControllerTests.swift"
			else:
				template_name = "TableViewControllerTests.swift"
			template = self.env.get_template(template_name)
			content = self._file_header(class_name)
			content += template.render(
				project=self.project,
				name=self.name
			)
			self._create_test_file(class_name, content)

		def _create_table_view_cell_tests(self):
			class_name = "{}CellTests".format(self.model_name)
			template_name = "TableViewCellTests.swift"
			template = self.env.get_template(template_name)
			content = self._file_header(class_name)
			content += template.render(
				project=self.project,
				model_name=self.model_name,
				properties=self.model.properties
			)
			self._create_test_file(class_name, content)


	#=================== DetailTemplate ===================


	class DetailTemplate(BaseTemplate):
		def __init__(self, model, options, name, project, developer, company, date):
			super(Template.DetailTemplate, self).__init__(name, project, developer, company, date)
			self.model = model
			self.options = options
			self.model_name = self.model.name
			self.model_variable = camel_case(self.model_name)

		def create_files(self):
			print(" ")
			self._make_dirs()
			self._create_view_model()
			self._create_navigator()
			self._create_use_case()
			self._create_view_controller()
			self._create_cells()
			self._create_view_model_tests()
			self._create_use_case_mock()
			self._create_navigator_mock()
			self._create_view_controller_tests()
			self._create_cells_tests()
			print(" ")

		def _create_view_model(self):
			class_name = self.name + "ViewModel"
			content = self._file_header(class_name)
			content += "struct {0}: ViewModelType {{\n\n".format(class_name)
			content += "    struct Input {\n"
			content += "        let loadTrigger: Driver<Void>\n"
			content += "    }\n\n"
			content += "    struct Output {\n"
			content += "        let cells: Driver<[CellType]>\n"
			content += "    }\n\n"
			content += "    enum CellType {\n"
			for p in self.model.properties:
				if p.name != "id":
					content += "        case {}({})\n".format(p.name, p.type.name)
			content += "    }\n\n"
			content += "    let navigator: {}NavigatorType\n".format(self.name)
			content += "    let useCase: {}UseCaseType\n".format(self.name)
			content += "    let {}: {}\n\n".format(self.model_variable, self.model_name)
			content += "    func transform(_ input: Input) -> Output {\n"
			content += "        let {} = input.loadTrigger\n".format(self.model_variable)
			content += "            .map {{ self.{} }}\n".format(self.model_variable)
			content += "        let cells = {}\n".format(self.model_variable)
			content += "            .map {{ {} -> [CellType] in\n".format(self.model_variable)
			content += "                var cells = [CellType]()\n"
			for p in self.model.properties:
				if p.name != "id":
					content += "                cells.append(CellType.{}({}.{}))\n".format(p.name, self.model_variable, p.name)
			content += "                return cells\n"
			content += "            }\n"
			content += "        return Output(cells: cells)\n"
			content += "    }\n"
			content += "}\n"
			file_name = class_name + ".swift"
			file_path = "{}/{}.swift".format(self.name, class_name)
			self._create_file(file_path, file_name, content)

		def _create_navigator(self):
			class_name = self.name + "Navigator"
			protocol_name = class_name + "Type"
			content = self._file_header(class_name)
			content += "protocol {}NavigatorType {{\n".format(self.name)
			content += "    func to{}({}: {})\n".format(self.name, self.model_variable, self.model_name)
			content += "}\n\n"
			content += "struct {}Navigator: {}NavigatorType {{\n".format(self.name, self.name)
			content += "    unowned let navigationController: UINavigationController\n\n"
			content += "    func to{}({}: {}) {{\n".format(self.name, self.model_variable, self.model_name)
			content += "        let useCase = {}UseCase()\n".format(self.name)
			content += "        let vm = {}ViewModel(navigator: self, useCase: useCase, {}: {})\n".format(self.name, self.model_variable, self.model_variable)
			content += "        let vc = {}ViewController.instantiate()\n".format(self.name)
			content += "        vc.bindViewModel(to: vm)\n"
			content += "        navigationController.pushViewController(vc, animated: true)\n"
			content += "    }\n"
			content += "}\n"
			file_name = class_name + ".swift"
			file_path = "{}/{}.swift".format(self.name, class_name)
			self._create_file(file_path, file_name, content)

		def _create_view_controller(self):
			class_name = self.name + "ViewController"
			content = self._file_header(class_name)
			content += "import UIKit\nimport Reusable\n\n"
			content += "final class {}: UIViewController, BindableType {{\n\n".format(class_name)
			content += "    @IBOutlet weak var tableView: UITableView!\n"
			content += "    var viewModel: {}ViewModel!\n\n".format(self.name)
			content += "    override func viewDidLoad() {\n"
			content += "        super.viewDidLoad()\n"
			content += "        configView()\n"
			content += "    }\n\n"
			content += "    private func configView() {\n"
			content += "        tableView.do {\n"
			content += "            $0.estimatedRowHeight = 550\n"
			content += "            $0.rowHeight = UITableViewAutomaticDimension\n"
			for p in self.model.properties:
				if p.name != "id":
					content += "            $0.register(cellType: {}{}Cell.self)\n".format(self.model_name, p.name_title)
			content += "        }\n"
			content += "    }\n"
			content += "    deinit {\n"
			content += "        logDeinit()\n"
			content += "    }\n\n"
			content += "    func bindViewModel() {\n"
			content += "        let input = {}ViewModel.Input(loadTrigger: Driver.just(()))\n".format(self.name)
			content += "        let output = viewModel.transform(input)\n"
			content += "        output.cells\n"
			content += "            .drive(tableView.rx.items) { tableView, index, cellType in\n"
			content += "                let indexPath = IndexPath(row: index, section: 0)\n"
			content += "                switch cellType {\n"
			for p in self.model.properties:
				if p.name != "id":
					content += "                case let .{}({}):\n".format(p.name, p.name)
					content += "                    return tableView.dequeueReusableCell(\n"
					content += "                        for: indexPath,\n"
					content += "                        cellType: {}{}Cell.self)\n".format(self.model_name, p.name_title)
			content += "                }\n"
			content += "            }\n"
			content += "            .disposed(by: rx.disposeBag)\n"
			content += "    }\n\n}\n\n"
			content += "// MARK: - StoryboardSceneBased\n"
			content += "extension {}ViewController: StoryboardSceneBased {{\n".format(self.name)
			content += "    static var sceneStoryboard = UIStoryboard()\n"
			content += "}\n"
			file_name = class_name + ".swift"
			file_path = "{}/{}.swift".format(self.name, class_name)
			self._create_file(file_path, file_name, content)

		def _create_cells(self):
			for p in self.model.properties:
				if p.name != "id":
					self._create_cell(p)

		def _create_cell(self, property):
			class_name = "{}{}Cell".format(self.model_name, property.name_title)
			content = self._file_header(class_name)
			content += "import UIKit\nimport Reusable\n\n"
			content += "final class {}{}Cell: UITableViewCell, NibReusable {{\n".format(self.model_name, property.name_title)
			if property.is_url:
				content += "    @IBOutlet weak var {}ImageView: UIImageView!\n".format(property.name)
			else:
				content += "    @IBOutlet weak var {}Label: UILabel!\n".format(property.name)
			content += "}\n"
			file_name = class_name + ".swift"
			file_path = "{}/{}.swift".format(self.name, class_name)
			self._create_file(file_path, file_name, content)

		def _create_view_model_tests(self):
			class_name = self.name + "ViewModelTests"
			content = self._file_header(class_name)
			content += "@testable import {}\n".format(self.project)
			content += "import XCTest\nimport RxSwift\nimport RxBlocking\n\n"
			content += "final class {}ViewModelTests: XCTestCase {{\n\n".format(self.name)
			content += "    private var viewModel: {}ViewModel!\n".format(self.name)
			content += "    private var navigator: {}NavigatorMock!\n".format(self.name)
			content += "    private var useCase: {}UseCaseMock!\n".format(self.name)
			content += "    private var disposeBag: DisposeBag!\n"
			content += "    private var input: {}ViewModel.Input!\n".format(self.name)
			content += "    private var output: {}ViewModel.Output!\n".format(self.name)
			content += "    private let loadTrigger = PublishSubject<Void>()\n\n"
			content += "    override func setUp() {\n"
			content += "        super.setUp()\n"
			content += "        navigator = {}NavigatorMock()\n".format(self.name)
			content += "        useCase = {}UseCaseMock()\n".format(self.name)
			content += "        viewModel = {}ViewModel(navigator: navigator, useCase: useCase, {}: {}())\n".format(self.name, self.model_variable, self.model_name)
			content += "        disposeBag = DisposeBag()\n"
			content += "        input = {}ViewModel.Input(\n".format(self.name)
			content += "            loadTrigger: loadTrigger.asDriverOnErrorJustComplete()\n"
			content += "        )\n"
			content += "        output = viewModel.transform(input)\n"
			content += "        output.cells.drive().disposed(by: disposeBag)\n"
			content += "    }\n\n"
			content += "    func test_loadTriggerInvoked_createCells() {\n"
			content += "        // act\n"
			content += "        loadTrigger.onNext(())\n"
			content += "        let cells = try? output.cells.toBlocking(timeout: 1).first()\n\n"
			content += "        // assert\n"
			content += "        XCTAssertNotEqual(cells??.count, 0)\n"
			content += "    }\n\n"
			content += "}\n"
			file_name = class_name + ".swift"
			file_path = "{}/Test/{}.swift".format(self.name, class_name)
			self._create_file(file_path, file_name, content)

		def _create_navigator_mock(self):
			class_name = self.name + "NavigatorMock"
			content = self._file_header(class_name)
			content += "@testable import {}\n\n".format(self.project)
			content += "final class {}NavigatorMock: {}NavigatorType {{\n".format(self.name, self.name)
			content += "    func to{}({}: {}) {{\n\n".format(self.name, self.model_variable, self.model_name)
			content += "    }\n"
			content += "}\n"
			file_name = class_name + ".swift"
			file_path = "{}/Test/{}.swift".format(self.name, class_name)
			self._create_file(file_path, file_name, content)

		def _create_view_controller_tests(self):
			class_name = self.name + "ViewControllerTests"
			content = self._file_header(class_name)
			content += "@testable import {}\n".format(self.project)
			content += "import XCTest\nimport Reusable\n\n"
			content += "final class {0}: XCTestCase {{\n\n".format(class_name)
			content += "    private var viewController: {}ViewController!\n\n".format(self.name)
			content += "    override func setUp() {\n"
			content += "        super.setUp()\n"
			content += "        viewController = {}ViewController.instantiate()\n".format(self.name)
			content += "    }\n\n"
			content += "    func test_ibOutlets() {\n"
			content += "        _ = viewController.view\n"
			content += "        XCTAssertNotNil(viewController.tableView)\n"
			content += "    }\n"
			content += "}\n"
			file_name = class_name + ".swift"
			file_path = "{}/Test/{}.swift".format(self.name, class_name)
			self._create_file(file_path, file_name, content)

		def _create_cells_tests(self):
			class_name = "{}CellsTests".format(self.name)
			content = self._file_header(class_name)
			content += "@testable import {}\n".format(self.project)
			content += "import XCTest\n\n"
			content += "final class {0}: XCTestCase {{\n\n".format(class_name)
			for p in self.model.properties:
				if p.name != "id":
					content += "    private var {}Cell: {}{}Cell!\n".format(p.name, self.model_name, p.name_title)
			content += "\n"
			content += "    override func setUp() {\n"
			content += "        super.setUp()\n"
			for p in self.model.properties:
				if p.name != "id":
					content += "        {}Cell = {}{}Cell.loadFromNib()\n".format(p.name, self.model_name, p.name_title)
			content += "    }\n\n"
			content += "    func test_iboutlets() {\n"
			for p in self.model.properties:
				if p.name != "id":
					content += "        XCTAssertNotNil({}Cell.{}Label)\n".format(p.name, p.name)
			content += "    }\n"
			content += "}\n"
			file_name = class_name + ".swift"
			file_path = "{}/Test/{}.swift".format(self.name, class_name)
			self._create_file(file_path, file_name, content)


	#=================== StaticDetailTemplate ===================


	class StaticDetailTemplate(DetailTemplate):

		def create_files(self):
			print(" ")
			self._make_dirs()
			self._create_view_model()
			self._create_navigator()
			self._create_use_case()
			self._create_view_controller()
			self._create_view_model_tests()
			self._create_use_case_mock()
			self._create_navigator_mock()
			self._create_view_controller_tests()
			self._create_cells_tests()
			print(" ")

		def _create_view_model(self):
			class_name = self.name + "ViewModel"
			content = self._file_header(class_name)
			content += "struct {}ViewModel: ViewModelType {{\n\n".format(self.name)
			content += "    struct Input {\n"
			content += "        let loadTrigger: Driver<Void>\n"
			content += "    }\n\n"
			content += "    struct Output {\n"
			content += "        let name: Driver<String>\n"
			content += "        let price: Driver<Double>\n"
			content += "    }\n\n"
			content += "    let navigator: {}NavigatorType\n".format(self.name)
			content += "    let useCase: {}UseCaseType\n".format(self.name)
			content += "    let {}: {}\n\n".format(self.model_variable, self.model_name)
			content += "    func transform(_ input: Input) -> Output {\n"
			content += "        let {} = input.loadTrigger\n".format(self.model_variable)
			content += "            .map {{ self.{} }}\n".format(self.model_variable)
			for p in self.model.properties:
				if p.name != "id":
					content += "        let {} = {}.map {{ $0.{} }}\n".format(p.name, self.model_variable, p.name)
			outputs = []
			for p in self.model.properties:
				if p.name != "id":
					output = "            {}: {}".format(p.name, p.name)
					outputs.append(output)
			content += "        return Output(\n"
			content += ",\n".join(outputs)
			content += "\n"
			content += "        )\n"
			content += "    }\n"
			content += "}\n"
			file_name = class_name + ".swift"
			file_path = "{}/{}.swift".format(self.name, class_name)
			self._create_file(file_path, file_name, content)

		def _create_view_controller(self):
			class_name = self.name + "ViewController"
			content = self._file_header(class_name)
			content += "import UIKit\nimport Reusable\n\n"
			content += "final class {}ViewController: UITableViewController, BindableType {{\n\n".format(self.name)
			for p in self.model.properties:
				if p.name != "id":
					if p.is_url:
						content += "    @IBOutlet weak var {}ImageView: UIImageView!\n".format(p.name)
					else:
						content += "    @IBOutlet weak var {}Label: UILabel!\n".format(p.name)
			content += "\n"
			content += "    var viewModel: {}ViewModel!\n\n".format(self.name)
			content += "    override func viewDidLoad() {\n"
			content += "        super.viewDidLoad()\n"
			content += "    }\n\n"
			content += "    deinit {\n"
			content += "        logDeinit()\n"
			content += "    }\n\n"
			content += "    func bindViewModel() {\n"
			content += "        let input = {}ViewModel.Input(\n".format(self.name)
			content += "            loadTrigger: Driver.just(())\n"
			content += "        )\n"
			content += "        let output = viewModel.transform(input)\n"
			for p in self.model.properties:
				if p.name != "id":
					content += "        output.{}\n".format(p.name)
					content += "            .drive()\n"
					content += "            .disposed(by: rx.disposeBag)\n"
			content += "    }\n"
			content += "}\n"
			content += "// MARK: - StoryboardSceneBased\n"
			content += "extension {}ViewController: StoryboardSceneBased {{\n".format(self.name)
			content += "    static var sceneStoryboard = UIStoryboard()\n"
			content += "}\n"
			file_name = class_name + ".swift"
			file_path = "{}/{}.swift".format(self.name, class_name)
			self._create_file(file_path, file_name, content)

		def _create_view_model_tests(self):
			class_name = self.name + "ViewModelTests"
			content = self._file_header(class_name)
			content += "@testable import {}\n".format(self.project)
			content += "import XCTest\nimport RxSwift\nimport RxBlocking\n\n"
			content += "final class {}ViewModelTests: XCTestCase {{\n\n".format(self.name)
			content += "    private var viewModel: {}ViewModel!\n".format(self.name)
			content += "    private var navigator: {}NavigatorMock!\n".format(self.name)
			content += "    private var useCase: {}UseCaseMock!\n".format(self.name)
			content += "    private var disposeBag: DisposeBag!\n"
			content += "    private var input: {}ViewModel.Input!\n".format(self.name)
			content += "    private var output: {}ViewModel.Output!\n".format(self.name)
			content += "    private let loadTrigger = PublishSubject<Void>()\n\n"
			content += "    override func setUp() {\n"
			content += "        super.setUp()\n"
			content += "        navigator = {}NavigatorMock()\n".format(self.name)
			content += "        useCase = {}UseCaseMock()\n".format(self.name)
			content += "        viewModel = {}ViewModel(navigator: navigator, useCase: useCase, {}: {}())\n".format(self.name, self.model_variable, self.model_name)
			content += "        disposeBag = DisposeBag()\n"
			content += "        input = {}ViewModel.Input(\n".format(self.name)
			content += "            loadTrigger: loadTrigger.asDriverOnErrorJustComplete()\n"
			content += "        )\n"
			content += "        output = viewModel.transform(input)\n"
			for p in self.model.properties:
				if p.name != "id":
					content += "        output.{}.drive().disposed(by: disposeBag)\n".format(p.name)
			content += "    }\n\n"
			content += "    func test_loadTriggerInvoked_createCells() {\n"
			content += "        // act\n"
			content += "        loadTrigger.onNext(())\n"
			for p in self.model.properties:
				if p.name != "id":
					content += "        let {} = try? output.{}.toBlocking(timeout: 1).first()\n".format(p.name, p.name)
			content += "\n"
			content += "        // assert\n"
			content += "        XCTAssert(true)\n"
			content += "    }\n\n"
			content += "}\n"
			file_name = class_name + ".swift"
			file_path = "{}/Test/{}.swift".format(self.name, class_name)
			self._create_file(file_path, file_name, content)

		def _create_view_controller_tests(self):
			class_name = self.name + "ViewControllerTests"
			content = self._file_header(class_name)
			content += "@testable import {}\n".format(self.project)
			content += "import XCTest\nimport Reusable\n\n"
			content += "final class {0}: XCTestCase {{\n\n".format(class_name)
			content += "    private var viewController: {}ViewController!\n\n".format(self.name)
			content += "    override func setUp() {\n"
			content += "        super.setUp()\n"
			content += "        viewController = {}ViewController.instantiate()\n".format(self.name)
			content += "    }\n\n"
			content += "    func test_ibOutlets() {\n"
			content += "        _ = viewController.view\n"
			content += "        XCTAssertNotNil(viewController.tableView)\n"
			for p in self.model.properties:
				if p.name != "id":
					if p.is_url:
						content += "        XCTAssertNotNil(viewController.{}ImageView)\n".format(p.name)
					else:
						content += "        XCTAssertNotNil(viewController.{}Label)\n".format(p.name)
			content += "    }\n"
			content += "}\n"
			file_name = class_name + ".swift"
			file_path = "{}/Test/{}.swift".format(self.name, class_name)
			self._create_file(file_path, file_name, content)

#=================== Commands ===================

class Commands:
	HELP = "help"
	HEADER = "header"
	TEMPLATE = "create"


class HelpCommand(object):
	def __init__(self):
		super(HelpCommand, self).__init__()
		
	def show_help(self):
		help = "iTools commands:\n"
		help += format("   help", "<15") + "Show help\n"
		help += format("   header", "<15") + "Update file header info\n"
		help += format("   create", "<15") + "Generate template files\n"
		help += "\n"
		help += "Get help on a command: python tempate.py help [command]\n"
		print(help)


class FileHeaderCommand(object):
	def __init__(self):
		super(FileHeaderCommand, self).__init__()

	def update_file_header(self):
		project = raw_input('Enter project name: ')
		developer = raw_input('Enter developer name: ')
		company = raw_input('Enter company name: ')
		content = "\n".join([project, developer, company])
		with open(FILE_HEADER, "w") as f:	
			f.write(content)
		return (project, developer, company)


class TemplateCommmand(object):
	def __init__(self, template_name, scene_name, options):
		super(TemplateCommmand, self).__init__()
		self.template_name = template_name
		self.scene_name = scene_name
		self.options = options

	def create_files(self):
		try:
			with open(FILE_HEADER) as f:
				content = f.readlines()
				info = [x.strip() for x in content]
				project = info[0]
				developer = info[1]
				company = info[2]
		except:
			project, developer, company = FileHeaderCommand().update_file_header()
		now = datetime.now()
		date = "{}/{}/{}".format(now.month, now.day, now.strftime("%y"))
		if self.template_name == Template.TemplateType.BASE:
			template = Template.BaseTemplate(self.scene_name, project, developer, company, date)
			template.create_files()
			print("Finish!")
		elif self.template_name == Template.TemplateType.LIST:
			model_text = pasteboard_read()
			# try:
			model = Template().parse_model(model_text)
			template = Template.ListTemplate(model, self.options, self.scene_name, project, developer, company, date)
			template.create_files()
			print("Finish!")
			# except:
			# 	print('Invalid model text in clipboard.')
		elif self.template_name == Template.TemplateType.DETAIL:
			model_text = pasteboard_read()
			try:
				model = Template().parse_model(model_text)
				if "--static" in self.options:
					template = Template.StaticDetailTemplate(model, self.options, self.scene_name, project, developer, company, date)
				else:
					template = Template.DetailTemplate(model, self.options, self.scene_name, project, developer, company, date)
				template.create_files()
				print("Finish!")
			except:
				print('Invalid model text in clipboard.')
		else:
			print("Invalid template name.")


#=================== Main ===================


def execute(args):
	command = args[0]
	if command == Commands.HELP:
		HelpCommand().show_help()
	elif command == Commands.HEADER:
		FileHeaderCommand().update_file_header()
	elif command == Commands.TEMPLATE:
		if len(args) >= 3:
			template_name = args[1]
			scene_name = args[2]
			options = args[3:]
			TemplateCommmand(template_name, scene_name, options).create_files()
		else:
			print("Invalid params.")
	else:
		print("'{}' is not a valid command. See 'python template.py help'.".format(command))

if len(sys.argv) > 1:
	execute(sys.argv[1:])
else:
	HelpCommand().show_help()


