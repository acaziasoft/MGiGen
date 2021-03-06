@testable import {{ project }}
import XCTest
import Reusable

final class {{ name }}ViewControllerTests: XCTestCase {
    var viewController: {{ name }}ViewController!

    override func setUp() {
        super.setUp()
        viewController = {{ name }}ViewController.instantiate()
    }

    func test_ibOutlets() {
        _ = viewController.view
        XCTAssertNotNil(viewController.usernameTextField)
        XCTAssertNotNil(viewController.usernameValidationLabel)
        XCTAssertNotNil(viewController.passwordTextField)
        XCTAssertNotNil(viewController.passwordValidationLabel)
        XCTAssertNotNil(viewController.loginButton)
    }
}
